# Build FFmpeg (Windows)

## Requirements

- 10GB of free space.
- A 64-bit Intel machine with at least 8GB of RAM.
- An appropriate version of Visual Studio, as described below.
- Windows 8.1 or newer.

## Install deps
### Open a **cmd** as Admin

#### Install chocolatey
	@powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))" && SET PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin

#### Install Git
	choco install git

#### Install node
	choco install node

#### Install VisualStudio 2019
[Download Visualstudio 2017](https://docs.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio)
> Chromium requires Visual Studio 2017 (>=15.7.2) to build, but VS2019 (>=16.0.0) is preferred. The clang-cl compiler is used but Visual Studio's header files, libraries, and some tools are required. Visual Studio Community Edition should work if its license is appropriate for you. You must install the “Desktop development with C++” component and the “MFC/ATL support” sub-components. This can be done from the command line by passing these arguments to the Visual Studio installer 

	PATH_TO_INSTALLER.EXE ^
    --add Microsoft.VisualStudio.Workload.NativeDesktop ^
    --add Microsoft.VisualStudio.Component.VC.ATLMFC ^
    --includeRecommended

> You must have the version **10.0.18362** or higher Windows 10 SDK installed. This can be installed separately or by checking the appropriate box in the Visual Studio Installer.

> The SDK Debugging Tools must also be installed. If the Windows 10 SDK was installed via the Visual Studio installer, then they can be installed by going to: Control Panel → Programs → Programs and Features → Select the “Windows Software Development Kit” → Change → Change → Check “Debugging Tools For Windows” → Change. Or, you can download the standalone SDK installer and use it to install the Debugging Tools

## Build ffmpeg.dll

This is the default behaviour, does not require additional steps, just run it and tadaaaa :tada:...

	git clone https://github.com/iteufel/nwjs-ffmpeg-prebuilt.git
	cd nwjs-ffmpeg-prebuilt

	//Build ffmpeg ia32
	node build --arch=x86

	//Build ffmpeg x64
	node build --arch=x64
