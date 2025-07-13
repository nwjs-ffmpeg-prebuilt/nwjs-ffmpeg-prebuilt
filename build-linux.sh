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
[linux-x64]='-fno-math-errno -fno-signed-zeros -fomit-frame-pointer'
[linux-ia32]='-m32 -fno-math-errno -fno-signed-zeros -fomit-frame-pointer'
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
  --extra-cflags="-O3 -pipe -fno-plt -flto=auto ${extcflags["$2"]}" \
  --extra-ldflags="${extldflags["$2"]}" \
  ${ffbuildflags["$2"]} \
  --enable-{pic,asm,hardcoded-tables} \
  --prefix="${srcdir}/release"

  make -j3 install

cd ../release
declare -A gccflag=(
[linux-x64]='-Wl,-u,avutil_version -lm -Wl,-Bsymbolic'
[linux-ia32]='-Wl,-u,avutil_version -lm -Wl,-Bsymbolic'
[osx-x64]=
[osx-arm64]=
[win-x64]='-lbcrypt'
[win-ia32]='-lbcrypt'
)
declare -A ldwholearchive=(
[linux-x64]='-Wl,--whole-archive '
[linux-ia32]='-Wl,--whole-archive '
[osx-x64]='-Wl,-force_load,'
[osx-arm64]='-Wl,-force_load,'
[win-x64]='-Wl,--whole-archive '
[win-ia32]='-Wl,--whole-archive '
)
declare -A ldnowholearchive=(
[linux-x64]='-Wl,--no-whole-archive '
[linux-ia32]='-Wl,--no-whole-archive '
[osx-x64]=
[osx-arm64]=
[win-x64]='-Wl,--no-whole-archive '
[win-ia32]='-Wl,--no-whole-archive '
)
declare -A libext=(
[linux-x64]=so
[linux-ia32]=so
[osx-x64]=dylib
[osx-arm64]=dylib
[win-x64]=dll
[win-ia32]=dll
)
${cc["$2"]} -shared  ${extldflags["$2"]} -flto=auto \
	${ldwholearchive["$2"]}lib/libavcodec.a \
	${ldwholearchive["$2"]}lib/libavformat.a \
	${ldnowholearchive["$2"]}lib/libavutil.a \
	${ldnowholearchive["$2"]}lib/libswresample.a \
	-lm ${gccflag["$2"]} -Wl,-s \
	-o libffmpeg.${libext["$2"]}
 zip -9 "$1"-"$2".zip libffmpeg.${libext["$2"]}
