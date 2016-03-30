#Build FFmpeg (Linux)

##Requirements

- 15GB of free space
- Ubuntu 14.04.4 or higher

##Install deps
	//Install Git
	apt-get update && apt-get install git

	//Install depot_tools
	git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git ~/.depot_tools
	echo "export PATH=\$PATH:$HOME/.depot_tools" >> ~/.bashrc
	echo "export PATH=\$PATH:$HOME/.depot_tools" >> ~/.zshrc

##Get the code
	//create the src dir
	mkdir -p ~/nwjs && cd ~/nwjs
	
	//create the gclient config
	$(curl -fsSL https://raw.githubusercontent.com/iteufel/nwjs-ffmpeg-prebuilt/master/gclient.config) > ~/nwjs/.gclient
	
	//Sync the code *This takes a while and a lot of space*
	gclient sync --with_branch_heads --force
	
##Build libffmpeg
	
	//install build deps
	./src/build/install-build-deps.sh
	
	export GYP_DEFINES="ffmpeg_branding=Chrome ffmpeg_component=shared_library"
	
	//Regenerate the gyp files
	gclient runhooks --force
	
	//Build libffmpeg
	ninja -C src/out/Release ffmpeg
