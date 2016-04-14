#Build FFmpeg (Windows)

##Requirements

- 15GB of free space
- Windows 10

##Install deps
	//Open a cmd as Admin

	//install chocolatey
	@powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))" && SET PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin
	
	//Install git
	choco install git
	
	//Install VisualStudio
	choco install visualstudio2015community -packageParameters "--Features MDDCPlusPlus,ToolsForWin81WP80WP81,VCMFCLibraries"
	
	//install Window 10 SDK
	choco install windows-sdk-10.0

	//Install depot_tools
	https://www.chromium.org/developers/how-tos/install-depot-tools
##Get the code
	//create the src dir
	mkdir -p ~/nwjs && cd ~/nwjs
	
	//create the gclient config
	$(curl -fsSL https://raw.githubusercontent.com/iteufel/nwjs-ffmpeg-prebuilt/master/gclient.config) > ~/nwjs/.gclient
	
	//Sync the code *This takes a while and a lot of space*
	gclient sync --with_branch_heads --force

##Build ffmpeg.dll x64
	//set some env
	set DEPOT_TOOLS_WIN_TOOLCHAIN=0
	set GYP_DEFINES=target_arch=x64 clang=0 ffmpeg_branding=Chrome ffmpeg_component=shared_library
	set GYP_MSVS_VERSION=2015
	
	//Regenerate gyp files
	gclient runhooks --force
	
	//Build ffmpeg x64
	ninja -C src/out/Release_x64 ffmpeg
	
##Build ffmpeg.dll ia32
	//set some env
	set DEPOT_TOOLS_WIN_TOOLCHAIN=0
	set GYP_DEFINES=target_arch=ia32 clang=0 ffmpeg_branding=Chrome ffmpeg_component=shared_library
	set GYP_MSVS_VERSION=2015
	
	//Regenerate gyp files
	gclient runhooks --force
	
	//Build ffmpeg ia32
	ninja -C src/out/Release ffmpeg