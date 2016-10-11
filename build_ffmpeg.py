#!/usr/bin/python

import re, os, platform, sys, getopt, shutil, io

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
  opts, args = getopt.getopt(sys.argv[1:], "hc", ["clean", "help", "proprietary_codecs", "target_platform=", "target_arch=", "nw_version="])
except getopt.GetoptError:
  usage()
  sys.exit(2)

if sys.platform.startswith('win'):
    host_platform = 'win'
elif sys.platform.startswith('linux'):
    host_platform = 'linux'
elif sys.platform.startswith('darwin'):
    host_platform = 'mac'

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

nw_version = '0.17.0'
target_arch = host_arch
target_platform = host_platform
proprietary_codecs = False

for opt, arg in opts:
  if opt in ("-h", "--help"):
    usage()
    sys.exit(0)
  elif opt in ("--platform_arch"):
    platform_arch = arg
  elif opt in ("--target_arch"):
    target_arch = arg
  elif opt in ("--nw_version"):
    nw_version = arg
  elif opt in ("-c", "--clean"):
    shutil.rmtree("build", ignore_errors=True)
  elif opt in ("--proprietary_codecs"):
    proprietary_codecs = True

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
sys.path.append(os.getcwd() + "/depot_tools")

#fix for gclient not found, seems like sys.path.append does not work but path is added
os.environ["PATH"] += os.pathsep + os.getcwd() + "/depot_tools"

if platform.system() == 'Windows' or 'CYGWIN_NT' in platform.system():
	os.environ["DEPOT_TOOLS_WIN_TOOLCHAIN"] = '0'

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
#copied from DEPS
min_vars = '''
vars = {
  'chromium_git':
    'https://chromium.googlesource.com',
}
'''

#deps
deps_list = {
  'buildtools'  : {
    'reg' : ur'buildtools\.git@(.+)\'',
    'repo': '/chromium/buildtools.git',
    'path': 'src/buildtools'
  },
  'gyp'  : {
    'reg' : ur'gyp\.git@(.+)\'',
    'repo': '/external/gyp.git',
    'path': 'src/tools/gyp'
  },
  'patched-yasm'  : {
    'reg' : ur'patched-yasm\.git@(.+)\'',
    'repo': '/chromium/deps/yasm/patched-yasm.git',
    'path': 'src/third_party/yasm/source/patched-yasm'
  },
  'ffmpeg'  : {
    'reg' : ur'ffmpeg\.git@(.+)\'',
    'repo': '/chromium/third_party/ffmpeg',
    'path': 'src/third_party/ffmpeg'
  },
}
min_deps = []
for k, v in deps_list.items():
  dep = grep_dep(v['reg'], v['repo'], v['path'])
  if dep is None:
    raise Exception("`%s` is not found in DEPS" % k)
  min_deps.append(dep)

min_deps = '''
deps = {
%s
}
''' % "\n".join(min_deps)

#hooks
#copied from DEPS
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
group("dummy") {
  deps = [
    "//third_party/ffmpeg"
  ]
}
'''
shutil.move('BUILD.gn', 'BUILD.gn.bak')
with open('BUILD.gn', 'w') as f:
  f.write(BUILD_gn)

#install linux dependencies
if platform.system() == 'Linux' and not os.path.isfile('buid_deps.ok'):
  os.system('./build/install-build-deps.sh --no-prompt --no-nacl --no-chromeos-fonts --no-syms')
  with io.FileIO("buid_deps.ok", "w") as file:
      file.write("Build dependencies already installed")

#gclient sync
os.system('gclient sync --no-history')

if proprietary_codecs:
    print "Building ffmpeg wiht proprietary codecs..."
    #going to ffmpeg folder
    os.chdir("third_party/ffmpeg")

    if not os.path.isfile('build_ffmpeg_patched.ok'):
        print "Applying codecs patch with ac3..."
        shutil.copy('../../patch/build_ffmpeg_proprietary_codecs.patch', 'third_party/ffmpeg/')
        #apply codecs path
        os.system('git apply --ignore-space-change --ignore-whitespace build_ffmpeg_proprietary_codecs.patch')
        with io.FileIO("build_ffmpeg_patched.ok", "w") as file:
            file.write("src/third_party/ffmpeg/chromium/scripts/build_ffmpeg.py already patched with proprietary codecs")

    print "Building ffmpeg..."
    #build ffmpeg
    os.system('./chromium/scripts/build_ffmpeg.py {0} {1}'.format(target_platform,target_arch))
    #copy the new generated ffmpeg config
    print "Copying new ffmpeg configuration..."
    os.system('./chromium/scripts/copy_config.sh')
    print "Creating a GYP include file for building FFmpeg from source..."
    #generate the ffmpeg configuration
    os.system('./chromium/scripts/generate_gyp.py')

    #back to src
    os.chdir("../..")

#generate ninja files
os.system('gn gen //out/nw "--args=is_debug=false is_component_ffmpeg=true target_cpu=\\\"%s\\\" is_official_build=true ffmpeg_branding=\\\"Chrome\\\""' % target_cpu)

#build ffmpeg
os.system("ninja -C out/nw ffmpeg")
