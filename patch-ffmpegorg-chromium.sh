#!/bin/bash -e
if [ "$1" != "ffmpegorg" ];then
echo This supports Linux-x64 only yet.
echo This patches to build libffmpeg.so from ffmpeg.org or ffmpeg.git .
echo If you really want to build from them, do patch-ffmpegorg-chromium.sh ffmpegorg before ./configure.
echo Do not use for chromium/third_pirty/ffmpeg !
exit 1
fi

curl https://gitlab.archlinux.org/archlinux/packaging/packages/ffmpeg/-/raw/main/0001-Add-av_stream_get_first_dts-for-Chromium.patch -o Add-av_stream_get_first_dts.patch
_chromium=137.0.7151.138
_chrff=$(curl -sL https://raw.githubusercontent.com/chromium/chromium/refs/tags/${_chromium}/DEPS | grep -oP "'ffmpeg_revision': '\K[0-9a-f]{40}'" | tr -d \')
curl https://chromium.googlesource.com/chromium/third_party/ffmpeg/+/${_chrff}/chromium/ffmpeg.sigs?format=TEXT -o ffmpeg.sigs.base64
mkdir -p chromium
base64 -d ffmpeg.sigs.base64 > chromium/ffmpeg.sigs
curl https://aur.archlinux.org/cgit/aur.git/plain/nolog.c?h=chromium-ffmpeg-codecs -o nolog.c # insecure source

# https://chromium.googlesource.com/chromium/third_party/ffmpeg/+/refs/heads/master/chromium/patches/README
patch -Np1 -i Add-av_stream_get_first_dts.patch # needed
sed -i.bak '/ff_aom_uninit_film_grain_params/d' libavcodec/h2645_sei.c
diff libavcodec/h2645_sei.c{.bak,}||:
sed -i.bak -E -e "/&ff_dirac_codec,/d" -e "/&ff_speex_codec,/d" \
-e "/&ff_theora_codec,/d" -e "/&ff_celt_codec,/d" -e "/&ff_old_dirac_codec,/d" libavformat/oggdec.c
diff libavformat/oggdec.c{.bak,}||:
sed -i.bak 's/^int av_sscanf(.*/#define av_sscanf sscanf/' libavutil/avstring.h # not only for -8 kb
diff libavutil/avstring.h{.bak,}||:
# CHROMIUM_NO_LOGGING
sed -i.bak -E \
  -e "/^void\s+av_log\s*\(.*\)\s*$/,/^\s*\}\s*$/d" \
  -e "/^void\s+av_log_once\s*\(.*\)\s*$/,/^\s*\}\s*$/d" \
  -e "/^void\s+av_vlog\s*\(.*\)\s*$/,/^\s*\}\s*$/d" \
 libavutil/log.c
cat nolog.c >> libavutil/log.c
