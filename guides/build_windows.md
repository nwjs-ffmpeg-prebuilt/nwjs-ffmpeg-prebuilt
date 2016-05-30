#Build FFmpeg (Windows)

##Requirements

- 3GB of free space
- Windows 7/8.1/10

##Install deps
	//Open a cmd as Admin

	//install chocolatey
	@powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))" && SET PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin
	
	//Install git
	choco install git
	
	//Install python
	choco install python
	
	//Install VisualStudio
	choco install visualstudio2015community -packageParameters "--Features MDDCPlusPlus,ToolsForWin81WP80WP81,VCMFCLibraries"

##Build ffmpeg.dll
	
	git clone https://github.com/iteufel/nwjs-ffmpeg-prebuilt.git
	cd nwjs-ffmpeg-prebuilt
	
	//Build ffmpeg ia32
	python build_ffmpeg.py --target_arch=ia32
	
	//Build ffmpeg x64
	python build_ffmpeg.py --target_arch=x64