#!/bin/bash -e
if [ "$1" != "ffmpegorg" ];then
echo This patches to build libffmpeg.so from ffmpeg.org or ffmpeg.git .
echo Do patch-ffmpegorg-chromium.sh ffmpegorg before ./configure
echo Do not use for chromium/third_pirty/ffmpeg
exit 1
fi
_url=https://chromium.googlesource.com/chromium/third_party/ffmpeg
curl https://gitlab.archlinux.org/archlinux/packaging/packages/ffmpeg/-/raw/2-7.1.1-1/0001-Add-av_stream_get_first_dts-for-Chromium.patch > av_stream_get_first_dts.patch
mkdir -p chromium/patches
curl ${_url}/+/refs/heads/master/chromium/ffmpeg.sigs?format=TEXT | base64 -d > chromium/ffmpeg.sigs

# ${_url}/+/refs/heads/master/chromium/patches/README
patch -Np1 -i av_stream_get_first_dts.patch # needed
# other patches are option to save binary size
# aac patches
curl ${_url}/+/bdcb0b447f433de3b69f0252732791b9f7e26f37/chromium/patches/README?format=TEXT | base64 -d > chromium/patches/README
curl ${_url}/+/a21071589971c54596dbbccbccdbac7bdd9d4e4c%5E%21/?format=TEXT | base64 -d > aac-save-RAM.patch
patch -Np1 -i aac-save-RAM.patch
curl ${_url}/+/30735bb16a66e84d6324b5858eef314822b6d419%5E%21/?format=TEXT | base64 -d > no-xheaac-parser.patch
patch -Np1 -i no-xheaac-parser.patch
# Remove ff_aom_uninit_film_grain_params
sed -i.bak '/ff_aom_uninit_film_grain_params/d' libavcodec/h2645_sei.c
diff libavcodec/h2645_sei.c{.bak,}||:
# Remove buggy parsers
sed -i.bak -E -e "/&ff_dirac_codec,/d" -e "/&ff_speex_codec,/d" \
-e "/&ff_theora_codec,/d" -e "/&ff_celt_codec,/d" -e "/&ff_old_dirac_codec,/d" libavformat/oggdec.c
diff libavformat/oggdec.c{.bak,}||:
# Remove av_sscanf
sed -i.bak 's/^int av_sscanf(.*/#define av_sscanf sscanf/' libavutil/avstring.h
$(command -v gsed||command -v sed) -i.bak -E "/^int\s+av_sscanf\s*\(.*\)\s*$/,/^\s*\}\s*$/d" libavutil/avsscanf.c
diff libavutil/avsscanf.c{.bak,}||:
# CHROMIUM_NO_LOGGING
_av_log=$(grep 'void av_log(' libavutil/log.c)
_av_log_once=$(grep 'void av_log_once(' libavutil/log.c)
_av_vlog=$(grep 'void av_vlog(' libavutil/log.c)
$(command -v gsed||command -v sed) -i.bak -E "/^void\s+(av_log|av_log_once|av_vlog)\s*\(.*\)\s*$/,/^\s*\}\s*$/d" libavutil/log.c
echo -e "${_av_log}{}\n${_av_log_once}{}\n${_av_vlog}{}" >> libavutil/log.c
diff libavutil/log.c{.bak,}||:
