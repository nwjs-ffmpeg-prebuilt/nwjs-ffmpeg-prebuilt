# Build FFmpeg (Linux)

## Requirements

- 10GB of free space
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
