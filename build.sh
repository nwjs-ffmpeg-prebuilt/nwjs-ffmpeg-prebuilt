#!/bin/bash -e
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

$(command -v ggrep||command -v grep)  -oP '\bav[a-z0-9_]*(?=\s*\()' chromium/ffmpeg.sigs > sigs.txt
echo -e "avformat_version\navutil_version\nff_h264_decode_init_vlc" >> sigs.txt # only for opera
echo -e "{\nglobal:\n$(sed 's/$/;/' sigs.txt)\nlocal:\n*;\n};" | tee export.map
# Use ffmpeg's native opus decoder not in kAllowedAudioCodecs at https://github.com/chromium/chromium/blob/main/media/ffmpeg/ffmpeg_common.cc
sed -i.bak "s/^ *\.p\.name *=.*/.p.name=\"libopus\",/" libavcodec/opus/dec.c
diff libavcodec/opus/dec.c{.bak,} || :
# https://chromium.googlesource.com/chromium/third_party/ffmpeg/+/refs/heads/master/
# BUILD.gn and chromium/config/Chrome/linux/x64/
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
  --cc="${cc["$1"]}" \
  --extra-cflags="-DCHROMIUM_NO_LOGGING" \
  --extra-cflags="-O3 -pipe -fno-plt -flto=auto ${extcflags["$1"]}" \
  --extra-ldflags="${extldflags["$1"]}" \
  ${ffbuildflags["$1"]} \
  --enable-{pic,asm,hardcoded-tables} \
  --libdir=/

  make DESTDIR=. install
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
[osx-arm64]=libffmpeg.dylib
[win-x64]=ffmpeg.dll
[win-ia32]=ffmpeg.dll
)

${cc["$1"]} -shared  ${extldflags["$1"]} -flto=auto \
	${startgroup["$1"]} libav{codec,format,util}.a libswresample.a ${endgroup["$1"]} \
	${gccflag["$1"]} -lm -Wl,-s \
	-o ${libname["$1"]}
