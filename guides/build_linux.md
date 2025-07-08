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

You can install our prebuilt at `/usr/lib/x86_64-linux-gnu/opera/lib_extra/libffmpeg.so`. However, Opera tries to load `/usr/lib/x86_64-linux-gnu/opera/libffmpeg.so` by `LD_PRELOAD` which potentially breaks many things including compabinity. So it is recommended to drop read permission from `/usr/lib/x86_64-linux-gnu/opera/libffmpeg.so` after you installed our prebuilt.

It is also recommended to use prebuilt corresponding with near Chromium version instead of latest version. Chromium version is avaiable at [link](opera:about) and you can fetch version of our prebuilt corresponding with major version of Chromium if `curl` and `jq` are usable at your system. To fetch version for Chromium M135, run
`curl -s https://nwjs.io/versions.json | jq -r 'limit(1; .versions[] | select(.components.chromium | startswith("135.")) | .version)'`.
