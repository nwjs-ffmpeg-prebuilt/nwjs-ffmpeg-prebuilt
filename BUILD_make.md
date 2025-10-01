
# FFmpeg prebuilt for Chromium based apps

FFmpeg prebuilt binaries with proprietary codecs and build script by `make` faster than official `gn` build. We also have some optimization not used by Chromium e.g. swapping decoders.

### Downloads
Prebuilt binaries are avaiable at [here](https://github.com/nwjs-ffmpeg-prebuilt/nwjs-ffmpeg-prebuilt/releases)

### Build

#### Required build tools

- Linux 64bit host (for Linux and Windows target)
- Xcode (for macOS target)
- make
- nasm
- gcc-multilib (for Linux ia32 target)
- gcc-mingw-w64-x86-64 (for WIndows x64 target)
- gcc-mingw-w64-i686 (for Windows ia32 target)
- curl jq tar

MSYS2 shell us recommended for building on Windows.
(Cross-built on Ubuntu is used at here currently).

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

Chromium supports decoding H.264 via macOS's API. We remove H.264 decoder by the reason.

#### Linux

User of Gentoo Linux or Arch Linux (AUR) is advised to use [ebuild](https://packages.gentoo.org/packages/media-video/ffmpeg-chromium) or [PKGBUILD](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=chromium-ffmpeg) instead of this project.

##### Opera Browser issue

Opera needs to care more than libavcodec version to use our binary.

It is recommended to install our binary at
`/usr/lib/x86_64-linux-gnu/opera/lib_extra/libffmpeg.so` and remove or drop read permission from default

``/usr/lib/x86_64-linux-gnu/opera/libffmpeg.so``

since Opera has bug that `LD_PRELOAD` buldled `.so` binary which breaks ABI compability.