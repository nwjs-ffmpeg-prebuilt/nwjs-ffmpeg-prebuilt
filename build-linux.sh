#!/bin/bash -e
# https://chromium.googlesource.com/chromium/third_party/ffmpeg/+/refs/heads/master/
# See BUILD.gn and chromium/config/Chrome/linux/x64/
declare -A ffbuildflags=(
[linux-x64]=
[linux-ia32]='--arch=x86 --enable-cross-compile'
[osx-x64]='--arch=x86_64 --enable-cross-compile'
[osx-arm64]='--arch=arm64'
[win-x64]='--arch=x86_64 --target-os=mingw32 --cross-prefix=x86_64-w64-mingw32-'
[win-ia32]='--arch=x86 --target-os=mingw32 --cross-prefix=i686-w64-mingw32-'
)
declare -A extcflags=(
[linux-x64]='-fno-math-errno -fno-signed-zeros -fno-semantic-interposition -fomit-frame-pointer'
[linux-ia32]='-m32 -fno-math-errno -fno-signed-zeros -fno-semantic-interposition -fomit-frame-pointer'
[osx-x64]='-arch x86_64 --target=x86_64-apple-macosx'
[osx-arm64]=
[win-x64]=
[win-ia32]=
)
declare -A extldflags=(
[linux-x64]='-Wl,-O1 -Wl,--sort-common -Wl,--as-needed -Wl,-z,relro -Wl,-z,now -Wl,-z,pack-relative-relocs'
[linux-ia32]='-m32 -Wl,-O1 -Wl,--sort-common -Wl,--as-needed -Wl,-z,relro -Wl,-z,now -Wl,-z,pack-relative-relocs'
[osx-x64]=
[osx-arm64]=
[win-x64]='-Wl,--nxcompat -Wl,--dynamicbase'
[win-ia32]='-Wl,--nxcompat -Wl,--dynamicbase'
)
declare -A cc=(
[linux-x64]=gcc
[linux-ia32]='gcc -m32'
[osx-x64]='clang -arch x86_64'
[osx-arm64]=clang
[win-x64]=x86_64-w64-mingw32-gcc
[win-ia32]=i686-w64-mingw32-gcc
)
srcdir=/tmp/nwff
mkdir -p ${srcdir}/chromium-ffmpeg
cd ${srcdir}/chromium-ffmpeg
# Fetch source
_chromium=$(curl -s https://nwjs.io/versions.json | jq -r ".versions[] | select(.version==\"v$1\") | .components.chromium")
# Use rg for macOS
_commit=$(curl -sL https://raw.githubusercontent.com/chromium/chromium/refs/tags/${_chromium}/DEPS | rg -oP "'ffmpeg_revision': '\K[0-9a-f]{40}'" | tr -d \')
git init
git remote add origin https://chromium.googlesource.com/chromium/third_party/ffmpeg
git fetch --depth=1 origin $_commit
git checkout $_commit
# List used functions
rg -oP -N '\bav[a-z0-9_]*(?=\s*\()' chromium/ffmpeg.sigs > ../sigs.txt
echo -e "avformat_version\navutil_version\nff_h264_decode_init_vlc" >> ../sigs.txt # only for opera
echo -e "{\nglobal:" > ../export.map
sed 's/$/;/' ${srcdir}/sigs.txt >> ../export.map
echo -e "local:\n*;\n};" >> ../export.map
# Use ffmpeg's native opus decoder not in kAllowedAudioCodecs at https://github.com/chromium/chromium/blob/main/media/ffmpeg/ffmpeg_common.cc
sed -i.bak "s/^ *\.p\.name *=.*/.p.name=\"libopus\",/" libavcodec/opus/dec.c
diff libavcodec/opus/dec.c{.bak,} || :
./configure \
  --disable-{debug,all,autodetect,doc,iconv,network,symver} \
  --disable-{error-resilience,faan,iamf} \
  --disable-{schannel,securetransport} \
  --enable-static --disable-shared \
  --enable-av{format,codec,util} \
  --enable-swresample \
  --enable-demuxer=ogg,matroska,webm,wav,flac,mp3,mov,aac \
  --enable-decoder=vorbis,opus,flac,pcm_s16le,mp3,aac,h264 \
  --enable-parser=aac,flac,h264,mpegaudio,opus,vorbis,vp9 \
  --cc="${cc["$2"]}" \
  --extra-cflags="-DCHROMIUM_NO_LOGGING" \
  --extra-cflags="-O3 -pipe -fno-plt -flto=auto ${extcflags["$2"]}" \
  --extra-ldflags="${extldflags["$2"]}" \
  ${ffbuildflags["$2"]} \
  --enable-{pic,asm,hardcoded-tables} \
  --libdir=/

  make -j3 DESTDIR=.. install

cd ..
_symbols=$(cat sigs.txt | awk '{print "-Wl,-u," $1}'|paste -sd ' ' -)
declare -A gccflag=(
[linux-x64]="${_symbols} -Wl,-u,avutil_version -Wl,--version-script=export.map -lm -Wl,-Bsymbolic"
[linux-ia32]="${_symbols} -Wl,-u,avutil_version -Wl,--version-script=export.map -lm -Wl,-Bsymbolic"
[osx-x64]=
[osx-arm64]=
[win-x64]="${_symbols} -Wl,-u,avutil_version -Wl,--version-script=export.map -lbcrypt"
[win-ia32]="${_symbols} -Wl,-u,avutil_version -Wl,--version-script=export.map -lbcrypt"
)
declare -A startgroup=(
[linux-x64]='-Wl,--start-group ' # space is not typo
[linux-ia32]='-Wl,--start-group '
[osx-x64]='-Wl,-force_load,'
[osx-arm64]='-Wl,-force_load,'
[win-x64]='-Wl,--start-group '
[win-ia32]='-Wl,--whole-archive ' # filtering of funcs cause few kb binary
)
declare -A endgroup=(
[linux-x64]='-Wl,--end-group'
[linux-ia32]='-Wl,--end-group'
[osx-x64]=
[osx-arm64]=
[win-x64]='-Wl,--end-group'
[win-ia32]='-Wl,--no-whole-archive'
)
declare -A libname=(
[linux-x64]=libffmpeg.so
[linux-ia32]=libffmpeg.so
[osx-x64]=libffmpeg.dylib
[osx-arm64]=kibffmpeg.dylib
[win-x64]=ffmpeg.dll
[win-ia32]=ffmpeg.dll
)

${cc["$2"]} -shared  ${extldflags["$2"]} -flto=auto \
	${startgroup["$2"]} libav{codec,format,util}.a libswresample.a ${endgroup["$2"]} \
	${gccflag["$2"]} -lm -Wl,-s \
	-o ${libname["$2"]}
 zip -9 "$1"-"$2".zip ${libname["$2"]}
