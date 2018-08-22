# Build FFmpeg (Linux)

## Requirements

- 3GB of free space
- Ubuntu 16.04.5 or higher

## Install deps
	//Install Git
	apt-get update && apt-get install git

## Build libffmpeg

	git clone https://github.com/iteufel/nwjs-ffmpeg-prebuilt.git
	cd nwjs-ffmpeg-prebuilt
	
	//Build ffmpeg ia32
	sudo python build_ffmpeg.py --target_arch=ia32
	
	//Build ffmpeg x64
	sudo python build_ffmpeg.py --target_arch=x64

## Known Problems

If you have issues building FFmpeg for ia32: [crbug.com/786760](https://crbug.com/786760).  
To fix this you can remove `HAVE_EBP_AVAILABLE` from `build/src/third_party/ffmpeg/BUILD.gn`
