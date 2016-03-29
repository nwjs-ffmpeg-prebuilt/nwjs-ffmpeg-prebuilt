#Build FFmpeg (OSX)

##Requirements

- 15GB of free space
- OSX 10.11.x

##Install deps
	//Install Xcode comandline tools
	xcode-select --install
	
	//Install Homebrew
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	
	//Install Git
	brew update && brew install git

	//Install depot_tools
	git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git ~/.depot_tools
	echo "export PATH=\$PATH:$HOME/.depot_tools" >> ~/.bash_profile
	echo "export PATH=\$PATH:$HOME/.depot_tools" >> ~/.zshrc

##Get the code
	//create the src dir
	mkdir -p ~/nwjs && cd ~/nwjs
	
	//create the gclient config
	curl -fsSL https://raw.githubusercontent.com/iteufel/nwjs-ffmpeg-prebuilt/master/gclient.config > ~/nwjs/.gclient
	
	//Sync the code *This takes a while and a lot of space*
	gclient sync --with_branch_heads --force
	
##Build libffmpeg

	//Apply the ffmpeg patch to enable Proprietary Codecs
	curl -fsSL https://raw.githubusercontent.com/iteufel/nwjs-ffmpeg-prebuilt/master/ffmpeg.patch | git apply --directory src/third_party/ffmpeg -
	
	//Regenerate the gyp files
	gclient runhooks --force
	
	//Build libffmpeg
	ninja -C src/out/Release ffmpeg
	