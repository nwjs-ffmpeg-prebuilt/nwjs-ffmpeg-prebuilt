# Build FFmpeg (OSX)

## Requirements

- 15GB of free space
- A 64-bit Intel Mac running 10.15.4+.

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
