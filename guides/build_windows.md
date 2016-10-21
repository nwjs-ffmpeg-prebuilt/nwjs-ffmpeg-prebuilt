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

##Build ffmpeg.dll (WHITOUT proprietary codecs)

This is the default behaviour, does not require additional steps, just run it and tadaaaa :tada:...

	git clone https://github.com/iteufel/nwjs-ffmpeg-prebuilt.git
	cd nwjs-ffmpeg-prebuilt

	//Build ffmpeg ia32
	python build_ffmpeg.py --target_arch=ia32

	//Build ffmpeg x64
	python build_ffmpeg.py --target_arch=x64

##Build ffmpeg.dll (WITH proprietary codecs)

The build procedure for Windows is a little bit complex and require additional steps to generate the FFmpeg library. Unfortunately we can not generate the library natively, we need to use a CygWin environment and do a few tricks:

* Download and install the latest CygWin with the following packages :

	```yasm, make, diffutils, pkg-config, git.```.

	You can do it with the typical installation package manager or from the command line with a simple command :

	```setup-x86_64.exe -q -P yasm, make, diffutils, pkg-config, git``` (do not install python, this is important, CygWin will use the default installed Python on Windows machine)

* Setup the building environment: assuming you have installed VS2015 with choco in the previous steps, open a Windows console (CMD.exe) and type

	```
	C:\>cd %VS140COMNTOOLS%
	C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\Tools>cd ..\..\VC
	C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC>vcvarsall.bat [amd64, amd64_x86]
	```

	Don't close the console.

* Start CygWin sharing the previous environment variables:

	```
	C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC>cd C:\cygwin64\bin
	C:\cygwin64\bin>START mintty.exe -i /Cygwin-Terminal.ico -
	```

	The CygWin console will be shown.

	Don't close the console.

* From the CygWin console:

	```
 	mv /usr/bin/link.exe /usr/bin/link.exe.1 (to avoid conflicts with MSVC linker)
  git clone https://github.com/iteufel/nwjs-ffmpeg-prebuilt.git
	python build_ffmpeg.py -pc (default host architecture)
	or
	python build_ffmpeg.py -ta [ia32|x64] -pc
  ```
If you want to build for different architectures you must close CygWin and close the Windows CMD console, and repeat the above process in order to set the building environment values for the desired architecture.
