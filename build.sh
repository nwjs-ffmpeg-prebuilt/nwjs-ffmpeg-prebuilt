#!/bin/bash -e
# Do not use declare -A for old bash on macOS
case $1 in
linux-ia32) ffbuild="--arch=x86 --enable-cross-compile" ;;
osx-x64) ffbuild="--arch=x86_64 --enable-cross-compile --enable-audiotoolbox --enable-decoder=aac_at,mp3_at --disable-decoder=aac,mp3,h264" ;;
osx-arm64) ffbuild="--arch=arm64 --enable-audiotoolbox --enable-decoder=aac_at,mp3_at --disable-decoder=aac,mp3,h264" ;;# Chromium decodes H264 via videotoolbox
win-x64) ffbuild="--arch=x86_64 --target-os=mingw32 --cross-prefix=x86_64-w64-mingw32-" ;;
win-ia32) ffbuild="--arch=x86 --target-os=mingw32 --cross-prefix=i686-w64-mingw32-" ;;
esac

case $1 in
linux-x64) cflags="-fno-math-errno -fno-signed-zeros" ;;
linux-ia32) cflags="-m32 -fno-math-errno -fno-signed-zeros" ;;
osx-x64) cflags="-arch x86_64 --target=x86_64-apple-macosx" ;;
esac

case $1 in
linux-x64) ldflags="-Wl,-O1 -Wl,--sort-common -Wl,--as-needed -Wl,-z,relro -Wl,-z,now -Wl,-z,pack-relative-relocs" ;;
linux-ia32) ldflags="-m32 -Wl,-O1 -Wl,--sort-common -Wl,--as-needed -Wl,-z,relro -Wl,-z,now -Wl,-z,pack-relative-relocs" ;;
win-*) ldflags="-Wl,-O1 -Wl,--sort-common -Wl,--as-needed -Wl,--nxcompat -Wl,--dynamicbase" ;;
esac

case $1 in
linux-*|osx-arm64) cc=gcc ;; # symlink to clang at macOS
osx-x64) cc="clang -arch x86_64";;
linux-ia32) cc="gcc -m32" ;;
win-x64) cc=x86_64-w64-mingw32-gcc ;;
win-ia32) cc=i686-w64-mingw32-gcc ;;
esac

# support old grep on macOS
grep  -o '\bav[a-z0-9_]*(' chromium/ffmpeg.sigs | sed 's/(//' > sigs.txt
echo -e "avformat_version\navutil_version\nff_h264_decode_init_vlc" >> sigs.txt # only for opera
echo -e "{\nglobal:\n$(sed 's/$/;/' sigs.txt)\nlocal:\n*;\n};" | tee export.map
sed -e 's/^/_/' -e 's/_ff_h264_decode_init_vlc//' sigs.txt > _sigs.txt
# Use ffmpeg's native opus decoder not in kAllowedAudioCodecs at https://github.com/chromium/chromium/blob/main/media/ffmpeg/ffmpeg_common.cc
sed -i.bak "s/^ *\.p\.name *=.*/.p.name=\"libopus\",/" libavcodec/opus/dec.c
diff libavcodec/opus/dec.c{.bak,} || :
# Use osapi on macOS
sed -i.bak "/^ *\.p\.name *=.*/s/\"_at\"//g" libavcodec/audiotoolboxdec.c
diff libavcodec/audiotoolboxdec.c{.bak,}||:
# https://chromium.googlesource.com/chromium/third_party/ffmpeg/+/refs/heads/master/
# BUILD.gn and chromium/config/Chrome/linux/x64/
./configure \
  --disable-{debug,all,autodetect,doc,iconv,network,symver} \
  --disable-{error-resilience,faan,iamf} \
  --disable-{schannel,securetransport} \
  --enable-static --disable-shared \
  --enable-av{format,codec,util} \
  --enable-swresample \
  --enable-demuxer=ogg,matroska,wav,flac,mp3,mov,aac \
  --enable-decoder=vorbis,opus,flac,pcm_s16le,mp3,aac,h264 \
  --enable-parser=aac,flac,h264,mpegaudio,opus,vorbis,vp9 \
  --cc="$cc" \
  --extra-cflags="-DCHROMIUM_NO_LOGGING" \
  --extra-cflags="-O3 -pipe -fno-plt -fno-semantic-interposition -fomit-frame-pointer -flto=auto $cflags" \
  --extra-ldflags="$ldflags" \
  $ffbuild \
  --enable-{pic,asm,hardcoded-tables} \
  --libdir=/

  make DESTDIR=. install
_symbols=$(sed 's/^/-Wl,-u,/' sigs.txt | paste -sd " " -)
case $1 in
linux-*) ccunify="${_symbols} -Wl,--version-script=export.map -lm -Wl,-Bsymbolic" ;;
osx-*) ccunify="-framework AudioToolbox -Wl,-exported_symbols_list,_sigs.txt -dead_strip" ;;
win-x64) ccunify="${_symbols} -Wl,--version-script=export.map -lbcrypt";;
win-ia32) ccunify="${_symbols} -Wl,--version-script=export.map -lbcrypt -static-libgcc";;
esac

case $1 in
win-ia32)
startgroup='-Wl,--whole-archive'
endgroup='-Wl,--no-whole-archive'
;;
osx-*) startgroup='-Wl,-all_load' ;;
*)
startgroup='-Wl,--start-group'
endgroup='-Wl,--end-group'
;;
esac

case $1 in
osx-*) lib=libffmpeg.dylib ;;
win-*) lib=ffmpeg.dll ;;
*) lib=libffmpeg.so ;;
esac

$cc -shared  $ldflags -flto=auto \
	$startgroup libav{codec,format,util}.a libswresample.a $endgroup \
	$ccunify -lm -Wl,-s -o $lib
