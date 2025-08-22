
# FFmpeg prebuilt for Chromium based apps

FFmpeg prebuilt binaries with proprietary codecs and build instructions for Window, Linux and macOS.
We also have some optimization not used by Chromium source.

### Downloads
Prebuilt binaries are avaiable at [here](https://github.com/nwjs-ffmpeg-prebuilt/nwjs-ffmpeg-prebuilt/releases)

### Build

This project provides build script by GNU `make` instead of official `gn` build which takes too many time and disk space.

#### Required build tools

- Linux 64bit host (for Linux and Windows target)
- macOS 64bit host (for macOS target)
- nasm
- gcc-multilib (for Linux ia32 target)
- gcc-mingw-w64-x86-64 (for WIndows x64 target)
- gcc-mingw-w64-i686 (for Windows ia32 target)
- bash and grep (newer version, install from brew for macOS)
- curl jq tar

#### Usage:

You need major soname of libavcodec suitable for Chromium version:

```
NW_VERSION=0.101.2
CHROMIUM=$(curl -s https://nwjs.io/versions.json | jq -r ".versions[] | select(.version==\"v$NW_VERSION\") | .components.chromium")
_commit=$(curl -sL https://chromium.googlesource.com/chromium/src.git/+/refs/tags/${CHROMIUM}/DEPS?format=TEXT | base64 -d | grep -oP "'ffmpeg_revision': '\K[0-9a-f]{40}'" | tr -d \')
SO=$(curl -sL ${_url}/+/${_commit}/libavcodec/version_major.h?format=TEXT|base64 -d | grep -oP 'LIBAVCODEC_VERSION_MAJOR\s+\K\d+')
```

We can build ffmpeg from source of [chromium/third_pirty/ffmpeg](https://chromium.googlesource.com/chromium/third_party/ffmpeg/):

`curl https://chromium.googlesource.com/chromium/third_party/ffmpeg/+archive/${_commit}.tar.gz -o chromium-ffmpeg.tar.gz`

Run build script with suitable `MAKEFLAGS`:

`MAKEFLAGS=-j7 bash ./build.sh $TARGET`

where `$TARGET` is one of linux-x64, linux-ia32, win-x64, win-ia32, osx-arm64 or osx-x64.

### License and Patent Fee

#### License
Using AAC and H.264 codecs requires you to pay attention to the patent royalties and the license of the source code.
Consult a lawyer if you do not understand the licensing constraints and using patented media formats in your application.
For more information about the license of the source code, check [here](https://chromium.googlesource.com/chromium/third_party/ffmpeg.git/+/master/CREDITS.chromium).

### Platform specific notes

#### macOS

macOS have its own API for hardware decoding: H.264 is supported by Chromium itself and others are supported by ffmpeg.
We remove H.264 decoder and replaces AAC and MP3 decoder by those reasons. But we still builds parsers and demuxers which might still have patient issues.

#### Windows

Building binary on Windows host is not supported yet. Decoding AAC via OSAPI is also unsupported yet.

#### Linux

User of Gentoo Linux or Arch Linux (AUR) is advised to use [ebuild](https://packages.gentoo.org/packages/media-video/ffmpeg-chromium) or [PKGBUILD](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=chromium-ffmpeg) instead of this project.

##### Opera Browser issue

Opera needs to care more than libavcodec version to use our binary.

It is recommended to install our binary at
`/usr/lib/x86_64-linux-gnu/opera/lib_extra/libffmpeg.so` and remove or drop read permission from default

``/usr/lib/x86_64-linux-gnu/opera/libffmpeg.so``

since Opera has strange internal `LD_PRELOAD` for default binary which blocks our custom performance optimization, or simply breaks video play back.
