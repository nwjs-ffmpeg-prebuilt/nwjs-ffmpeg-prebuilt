# FFmpeg prebuilt for NW.js


FFMpeg prebuilt binaries with proprietary codecs and build instructions for window, linux and macos.


### Downloads (v0.37.4)
- Linux: [32bit](https://github.com/iteufel/nwjs-ffmpeg-prebuilt/releases/download/0.37.4/0.37.4-linux-ia32.zip) / [64bit](https://github.com/iteufel/nwjs-ffmpeg-prebuilt/releases/download/0.37.4/0.37.4-linux-x64.zip)
- Windows: [32bit](https://github.com/iteufel/nwjs-ffmpeg-prebuilt/releases/download/0.37.4/0.37.4-win-ia32.zip) / [64bit](https://github.com/iteufel/nwjs-ffmpeg-prebuilt/releases/download/0.37.4/0.37.4-win-x64.zip)
- Mac: [64bit](https://github.com/iteufel/nwjs-ffmpeg-prebuilt/releases/download/0.37.4/0.37.4-osx-x64.zip)

### Build

#### Usage:

build_ffmpeg.py [-h] [-c] [-nw NW_VERSION] [-ta TARGET_ARCH]
##### Arguments explanied:

-  *-h, --help* : Show the help message and exit
-  *-c, --clean* : Clean the workspace, removes downloaded source code
-  *-nw NW_VERSION, --nw_version NW_VERSION* : Build ffmpeg for the specified Nw.js version (latest from http://nwjs.io/versions.json if not specified) or branch
-  *-ta TARGET_ARCH, --target_arch TARGET_ARCH* : Target architecture, ia32, x64

#### Specific guides:

- [Windows guide](guides/build_windows.md)
- [Linux guide](guides/build_linux.md)
- [Mac guide](guides/build_mac.md)

You can get the FFmpeg source code from [here](https://chromium.googlesource.com/chromium/third_party/ffmpeg).

>### License and Patent Fee
> Using MP3 and H.264 codecs requires you to pay attention to the patent royalties and the license of the source code. Consult a lawyer if you do not understand the licensing constraints and using patented media formats in your application. For more information about the license of the source code, check [here](https://chromium.googlesource.com/chromium/third_party/ffmpeg.git/+/master/CREDITS.chromium).
