# Build FFmpeg (Linux)

## Requirements

- 15GB of free space
- Ubuntu 16.04.5 or higher
- Git
- node

## Build libffmpeg
	
	//Build ffmpeg x86
	npx nwjs-ffmpeg-prebuilt --arch x86
	
	//Build ffmpeg x86
	npx nwjs-ffmpeg-prebuilt --arch x64

#### Or

	git clone https://github.com/iteufel/nwjs-ffmpeg-prebuilt.git
	cd nwjs-ffmpeg-prebuilt
	npm i
	
	//Build ffmpeg x86
	sudo node build --arch x86
	
	//Build ffmpeg x64
	sudo node build --arch x64


## Known Problems

If you have issues building FFmpeg for ia32: [crbug.com/786760](https://crbug.com/786760).  
To fix this you can remove `HAVE_EBP_AVAILABLE` from `build/src/third_party/ffmpeg/BUILD.gn`

## Opera Browser issue

Opera needs binary with correct avcodec version. avcodec version is avaiable at release page.

1. Download binary from [here](https://github.com/nwjs-ffmpeg-prebuilt/nwjs-ffmpeg-prebuilt/releases) with avcodec62 or later.

2. Copy `libffmpeg.so` binary to:
```/usr/lib/x86_64-linux-gnu/opera/lib_extra/libffmpeg.so```
or
```/usr/lib/opera/lib_extra/libffmpeg.so```
(File path is depending on distributions. Put under `lib_extra`.)

3. Remove
```/usr/lib/x86_64-linux-gnu/opera/libffmpeg.so```
or
```/usr/lib/opera/libffmpeg.so```
since Opera has bug to `LD_PRELOAD` the binary which blocks optimizations of binary.

4. Restart your web browser.
