#!/usr/bin/python

import re, os, platform, sys, getopt, shutil, subprocess

def usage():
  print "Usage: build.py [options]"

def grep_dep(reg, repo, dir):
  pat = re.compile(reg)
  found = re.search(pat, deps_str)
  if found is None:
    return None
  head = found.group(1)
  return '''
  '%s':
    (Var(\"chromium_git\")) + '%s@%s',
''' % (dir, repo, head)

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

nw_version='0.17.0'
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
    shutil.rmtree("build", ignore_errors=True)

if target_arch == "ia32":
  target_cpu = "x86"
else:
  target_cpu = target_arch

try:
  os.mkdir("build")
except OSError:
  print "build is already created"

os.chdir("build")

shutil.rmtree("src/out", ignore_errors=True)

chromium_git = 'https://chromium.googlesource.com'
#clone depot_tools
os.system("git clone --depth=1 https://chromium.googlesource.com/chromium/tools/depot_tools.git")
os.environ["PATH"] = os.environ["PATH"] + ":" + os.getcwd() + "/depot_tools"

#create .gclient file
os.system("gclient config --unmanaged --name=src https://github.com/nwjs/chromium.src.git@tags/nw-v" + nw_version)

#clone chromium.src
os.system("git clone --depth=1 -b nw-v" + nw_version + " --single-branch https://github.com/nwjs/chromium.src.git src")

#overwrite DEPS file
os.chdir("src")
os.system("git reset --hard tags/nw-v" + nw_version)

shutil.rmtree("DPES.bak", ignore_errors=True)
shutil.rmtree("BUILD.gn.bak", ignore_errors=True)

with open('DEPS', 'r') as f:
  deps_str = f.read()

#vars
min_vars = '''
vars = {
  'chromium_git':
    'https://chromium.googlesource.com',
}
'''

#deps
min_deps = []
buildtools = grep_dep(ur'buildtools\.git@(.+)\'', '/chromium/buildtools.git', 'src/buildtools')
gyp = grep_dep(ur'gyp\.git@(.+)\'', '/external/gyp.git', 'src/tools/gyp')
yasm = grep_dep(ur'patched-yasm\.git@(.+)\'', '/chromium/deps/yasm/patched-yasm.git', 'src/third_party/yasm/source/patched-yasm')
ffmpeg = grep_dep(ur'ffmpeg\.git@(.+)\'', '/chromium/third_party/ffmpeg', 'src/third_party/ffmpeg')
if buildtools is None:
  raise Exception('`gyp` is not found in DEPS')
min_deps.append(buildtools)
if gyp is None:
  raise Exception('`gyp` is not found in DEPS')
min_deps.append(gyp)
if yasm is None:
  raise Exception('`yasm` is not found in DEPS')
min_deps.append(yasm)
if ffmpeg is None:
  raise Exception('`ffmpeg` is not found in DEPS')
min_deps.append(ffmpeg)
min_deps = '''
deps = {
%s
}
''' % "\n".join(min_deps)

#hooks
min_hooks = '''
hooks = [
  {
    'action': [
      'python',
      'src/build/linux/sysroot_scripts/install-sysroot.py',
      '--running-as-hook'
    ],
    'pattern':
      '.',
    'name':
      'sysroot'
  },
  {
    'action': [
      'python',
      'src/build/mac_toolchain.py'
    ],
    'pattern':
      '.',
    'name':
      'mac_toolchain'
  },
  {
    'action': [
      'python',
      'src/tools/clang/scripts/update.py',
      '--if-needed'
    ],
    'pattern':
      '.',
    'name':
      'clang'
  },
  {
    'action': [
      'download_from_google_storage',
      '--no_resume',
      '--platform=win32',
      '--no_auth',
      '--bucket',
      'chromium-gn',
      '-s',
      'src/buildtools/win/gn.exe.sha1'
    ],
    'pattern':
      '.',
    'name':
      'gn_win'
  },
  {
    'action': [
      'download_from_google_storage',
      '--no_resume',
      '--platform=darwin',
      '--no_auth',
      '--bucket',
      'chromium-gn',
      '-s',
      'src/buildtools/mac/gn.sha1'
    ],
    'pattern':
      '.',
    'name':
      'gn_mac'
  },
  {
    'action': [
      'download_from_google_storage',
      '--no_resume',
      '--platform=linux*',
      '--no_auth',
      '--bucket',
      'chromium-gn',
      '-s',
      'src/buildtools/linux64/gn.sha1'
    ],
    'pattern':
      '.',
    'name':
      'gn_linux64'
  },
  {
    'action': [
      'download_from_google_storage',
      '--no_resume',
      '--platform=darwin',
      '--no_auth',
      '--bucket',
      'chromium-libcpp',
      '-s',
      'src/third_party/libc++-static/libc++.a.sha1'
    ],
    'pattern':
      '.',
    'name':
      'libcpp_mac'
  },
]
'''

#overwrite DEPS
shutil.move('DEPS', 'DEPS.bak')
with open('DEPS', 'w') as f:
  f.write("%s\n%s\n%s" % (min_vars, min_deps, min_hooks))

#overwrite BUILD.gn
BUILD_gn = '''
action("dummy") {
  deps = [
    "//third_party/ffmpeg"
  ]
  script = "dummy"
  outputs = ["$target_gen_dir/dummy.txt"]
}
'''
shutil.move('BUILD.gn', 'BUILD.gn.bak')
with open('BUILD.gn', 'w') as f:
  f.write(BUILD_gn)

#install linux dependencies
if platform.system() == 'Linux':
  os.system('./build/install-build-deps.sh --no-prompt --no-nacl --no-chromeos-fonts --no-syms')

#gclient sync
os.system('gclient sync --no-history')

#generate ninja files
subprocess.call(['gn', 'gen', '//out/nw', '--args=is_debug=false is_component_ffmpeg=true target_cpu="%s" is_official_build=true ffmpeg_branding="Chrome"' % target_cpu], shell=True)

#build ffmpeg
os.system("ninja -C out/nw ffmpeg")