# Build FFmpeg (OSX)

## Requirements

- 10GB of free space
- OSX 10.13.x

## Install deps
	//Install Xcode comandline tools
	xcode-select --install
	
	//Install Homebrew
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	
	//Install Git & python
	brew update && brew install git python node

## Build libffmpeg
	git clone https://github.com/iteufel/nwjs-ffmpeg-prebuilt.git
	cd nwjs-ffmpeg-prebuilt
	npm i
	node build
	
####Or
    npx nwjs-ffmpeg-prebuilt
