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

Is some exceptional cases, the build doesn't work for Opera Browser for some unknown reason. In this specific cases,
you can just execute the following steps:

1. Build the project or download the latest version through this [link](https://github.com/nwjs-ffmpeg-prebuilt/nwjs-ffmpeg-prebuilt/releases/tag/0.72.0)

2. Unzip the compress file

3. Copy file to the following folder:
```bash
sudo cp /Downloads/cp 0.67.1-linux-x64/libffmpeg.so /usr/lib/x86_64-linux-gnu/opera/lib_extra/libffmpeg.so
```
Fedora users 
1. Copy file to the following folder:
```bash
sudo cp Downloads/libffmpeg.so /usr/lib64/opera/libffmpeg.so
```
4. Restart your web browser.
