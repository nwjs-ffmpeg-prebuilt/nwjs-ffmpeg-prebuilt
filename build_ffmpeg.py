#!/usr/bin/python

import re, os, platform, sys, getopt, shutil

def usage():
	print "Usage: build.py [options]"

try:                                
	opts, args = getopt.getopt(sys.argv[1:], "hc", ["clean", "help", "target_arch=", "nw_version="])
except getopt.GetoptError:
	usage()
	sys.exit(2)

if re.match(r'i.86', platform.machine()):
	host_arch = 'ia32'
elif platform.machine() == 'x86_64' or platform.machine() == 'AMD64':
	host_arch = 'x64'
elif platform.machine() == 'aarch64':
	host_arch = 'arm64'
elif platform.machine().startswith('arm'):
	host_arch = 'arm'
else:
	sys.exit(1)

nw_version='15'
target_arch=host_arch

for opt, arg in opts:
	if opt in ("-h", "--help"):
		usage()
		sys.exit(0)
	elif opt in ("--target_arch"):
		target_arch = arg 
	elif opt in ("--nw_version"):
		nw_version = arg 
	elif opt in ("-c", "--clean"): 
		shutil.rmtree("chromium.src", ignore_errors=True)
		shutil.rmtree("depot_tools", ignore_errors=True)

shutil.rmtree("chromium.src/out", ignore_errors=True)

chromium_git = 'https://chromium.googlesource.com'
#clone depot_tools
os.system("git clone --depth=1 https://chromium.googlesource.com/chromium/tools/depot_tools.git")
os.environ["PATH"] = os.environ["PATH"] + ":" + os.getcwd() + "/depot_tools"

#clone chromium.src
os.system("git clone --depth=1 -b nw" + nw_version + " --single-branch https://github.com/nwjs/chromium.src.git")
os.chdir('chromium.src')

deps_str = open('DEPS', 'r').read()

#clone gyp
gyp_pat = re.compile(ur'gyp\.git@(.+)\'')
gyp_head = re.search(gyp_pat, deps_str).group(1)
gyp_dep = chromium_git + '/external/gyp.git'
os.system("git clone --depth=1 -o " + gyp_head + " " + gyp_dep + " tools/gyp")

#clone patched-yasm
yasm_pat = re.compile(ur'patched-yasm\.git@(.+)\'')
yasm_head = re.search(yasm_pat, deps_str).group(1)
yasm_dep = chromium_git + '/chromium/deps/yasm/patched-yasm.git'
os.system("git clone --depth=1 -o " + yasm_head + " " + yasm_dep + " third_party/yasm/source/patched-yasm")

#clone ffmpeg
ffmpeg_pat = re.compile(ur'ffmpeg\.git@(.+)\'')
ffmpeg_head = re.search(ffmpeg_pat, deps_str).group(1)
ffmpeg_dep = chromium_git + '/chromium/third_party/ffmpeg'
os.system("git clone --depth=1 -o " + ffmpeg_head + " " + ffmpeg_dep + " third_party/ffmpeg")

#set some env
os.environ["GYP_GENERATORS"] = "ninja"
os.environ["PYTHONPATH"] = os.getcwd() + "/build"

if platform.system() == 'Windows' or 'CYGWIN_NT' in platform.system():
	os.environ["GYP_DEFINES"] = "branding=Chrome ffmpeg_component=shared_library clang=0 target_arch=" + target_arch
else:
	os.environ["GYP_DEFINES"] = "branding=Chrome ffmpeg_component=shared_library target_arch=" + target_arch

#install linux dependencies
if platform.system() == 'Linux':
	os.system('python build/linux/sysroot_scripts/install-sysroot.py --running-as-hook')

os.system('python tools/clang/scripts/update.py --if-needed')

#generate gypfiles
os.system('sh ./tools/gyp/gyp -I build/common.gypi --depth=. ./third_party/ffmpeg/ffmpeg.gyp')

#build ffmpeg
if target_arch == 'ia32' or platform.system() == 'Darwin':
	os.system('ninja -C out/Release ffmpeg')
else:
	os.system('ninja -C out/Release_x64 ffmpeg')
