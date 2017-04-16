# Build FFmpeg (Linux)

## Requirements

- 3GB of free space
- Ubuntu 14.04.4 or higher

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
