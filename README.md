
# FFmpeg prebuilt for NW.js


FFmpeg prebuilt binaries with proprietary codecs and build instructions for Window, Linux and macOS.


### Downloads
Downloads can be found [here](https://github.com/iteufel/nwjs-ffmpeg-prebuilt/releases)

### Build

#### Usage:

node build[-h] [-c] [--version NW_VERSION] [--arch TARGET_ARCH]
or
npx nwjs-ffmpeg-prebuilt [-h] [-c] [-d] [--get-download-url] [--version NW_VERSION] [--arch TARGET_ARCH]
##### Arguments explanied:

-  *-h, --help* : Show the help message and exit
-  *-c, --clean* : Clean the workspace, removes downloaded source code
-  *-v NW_VERSION, --version NW_VERSION* : Build ffmpeg for the specified Nw.js version (latest from http://nwjs.io/versions.json if not specified)
-  *-a TARGET_ARCH, --arch TARGET_ARCH* : Target architecture, x86, x64, arm
-  *-d, --download* : Download Prebuild binaries.
-  *-p, --platform* : Download platform, darwin, win, linux
-  *--get-download-url* : Get Download Url for Prebuild binaries
-  *-o, --out* : Output Directory

#### Specific guides:

- [Windows guide](guides/build_windows.md)
- [Linux guide](guides/build_linux.md)
- [Mac guide](guides/build_mac.md)

You can get the FFmpeg source code from [here](https://chromium.googlesource.com/chromium/third_party/ffmpeg).

>### License and Patent Fee
> Using AAC and H.264 codecs requires you to pay attention to the patent royalties and the license of the source code. Consult a lawyer if you do not understand the licensing constraints and using patented media formats in your application. For more information about the license of the source code, check [here](https://chromium.googlesource.com/chromium/third_party/ffmpeg.git/+/master/CREDITS.chromium).
