#!/usr/bin/python

import re
import os
import platform
import sys
import getopt
import shutil
import io
import argparse
import json
import urllib2
import subprocess
import textwrap
import traceback
import zipfile

from subprocess import *

PATH_BASE = os.path.abspath(os.path.dirname(sys.argv[0]))
PATH_BUILD = os.path.join(PATH_BASE, 'build')
PATH_DEPOT_TOOLS = os.path.join(PATH_BUILD, 'depot_tools')
PATH_SRC = os.path.join(PATH_BASE, 'build', 'src')
PATH_SRC_BUILD = os.path.join(PATH_SRC, 'build')
PATH_THIRD_PARTY_FFMPEG = os.path.join(PATH_SRC, 'third_party', 'ffmpeg')
PATH_OUT = os.path.join(PATH_SRC, 'out')
PATH_LIBRARY_OUT = os.path.join(PATH_OUT, 'nw')
PATH_RELEASES =  os.path.join(PATH_BASE, 'releases')

COLOR_ERROR = '\033[91m'
COLOR_OK = '\033[92m'
COLOR_WARNING = '\033[93m'
COLOR_INFO = '\033[94m'
COLOR_NORMAL = '\033[0m'

COLOR_NORMAL_WINDOWS = 7
COLOR_OK_WINDOWS = 10
COLOR_INFO_WINDOWS = 11
COLOR_ERROR_WINDOWS = 12
COLOR_WARNING_WINDOWS = 14


def main():

    nw_version = get_latest_stable_nwjs()
    host_platform = get_host_platform()
    target_arch = get_host_architecture()
    target_cpu = target_arch
    platform_release_name = get_platform_release_name(host_platform)
    
    if platform.system() == 'Linux':
      os.environ["LLVM_DOWNLOAD_GOLD_PLUGIN"] = "1"
    
    try:
        args = parse_args()
        if args.clean:
            response = raw_input('Are you sure you want to delete your workspace? (y/n):').lower()
            if response == 'y':
                print_info('Cleaning workspace...')
                shutil.rmtree('build', ignore_errors=True)
            else:
                print_info('Skipping workspace cleaning...')

        if args.nw_version:
            print_info('Setting nw version to ' + args.nw_version)
            nw_version = args.nw_version

        if args.target_arch:
            target_arch = args.target_arch

        if target_arch == 'ia32':
            target_cpu = 'x86'
        

        print_info('Building ffmpeg for {0} on {1} for {2}'.format(nw_version, host_platform, target_cpu))

        isVersion = bool(re.match(r"\d+\.\d+\.\d+", nw_version))

        create_directory(PATH_BUILD)

        clean_output_directory()

        setup_chromium_depot_tools(nw_version, isVersion)

        clone_chromium_source_code(nw_version, isVersion)

        reset_chromium_src_to_nw_version(nw_version, isVersion)

        generate_build_and_deps_files()

        install_build_deps()

        gclient_sync()

        patch_linux_sanitizer_ia32(target_cpu)

        build(target_cpu)

        zip_release_output_library(nw_version, platform_release_name, target_arch, get_out_library_path(host_platform), PATH_RELEASES)

        print_ok('DONE!!')

    except KeyboardInterrupt:
        print '\n\nShutdown requested... \x1b[0;31;40m' + 'exiting' + '\x1b[0m'
    except Exception:
        print_error (traceback.format_exc())
        sys.exit(1)


def patch_linux_sanitizer_ia32(target_cpu):
    host_platform = get_host_platform()
    if host_platform == 'linux':
        oldpath = os.getcwd()
        os.chdir(PATH_THIRD_PARTY_FFMPEG)
        os.system('git reset --hard')
        if target_cpu == 'x86':
            shutil.copy(os.path.join(PATH_BASE, 'patch', host_platform, 'sanitizer_ia32.patch'), os.getcwd())
            os.system('git apply --ignore-space-change --ignore-whitespace sanitizer_ia32.patch')
        os.chdir(oldpath)


def parse_args():
    parser = argparse.ArgumentParser(description='ffmpeg builder script.')
    parser.add_argument('-c', '--clean', help='Clean the workspace, removes downloaded source code', required=False, action='store_true')
    parser.add_argument('-nw', '--nw_version', help='Build ffmpeg for the specified Nw.js version or Branche', required=False)
    parser.add_argument('-ta', '--target_arch', help='Target architecture, ia32, x64', required=False)
    return parser.parse_args()


def grep_dep(reg, repo, dir, deps_str, opts):
    pat = re.compile(reg, opts)
    found = re.search(pat, deps_str)
    if found is None:
        return None
    head = found.group(1)
    return textwrap.dedent('''
      '%s':
        (Var(\"chromium_git\")) + '%s@%s',
    ''') % (dir, repo, head)


def get_host_platform():
    if platform.system() == 'Windows' or 'CYGWIN_NT' in platform.system():
        host_platform = 'win'
    elif platform.system() == 'Linux':
        host_platform = 'linux'
    elif platform.system() == 'Darwin':
        host_platform = 'mac'

    return host_platform


def get_host_architecture():
    if re.match(r'i.86', platform.machine()):
        host_arch = 'ia32'
    elif platform.machine() == 'x86_64' or platform.machine() == 'AMD64':
        host_arch = 'x64'
    elif platform.machine() == 'aarch64':
        host_arch = 'arm64'
    elif platform.machine().startswith('arm'):
        host_arch = 'arm'
    else:
        print_error('Unexpected host machine architecture, exiting...')
        sys.exit(1)

    return host_arch


def get_out_library_path(host_platform):
    if host_platform == 'win' or 'CYGWIN_NT' in platform.system():
        out_library_path = os.path.join(PATH_LIBRARY_OUT, 'ffmpeg.dll')
    elif host_platform == 'linux':
        out_library_path = os.path.join(PATH_LIBRARY_OUT, 'lib', 'libffmpeg.so')
    elif host_platform == 'mac':
        out_library_path = os.path.join(PATH_LIBRARY_OUT, 'libffmpeg.dylib')

    return out_library_path


def get_platform_release_name(host_platform):
    if host_platform == 'mac':
        platform_release_name = 'osx'
    else:
        platform_release_name = host_platform

    return platform_release_name


def get_latest_stable_nwjs():
    # We always build ffmpeg for the latest stable
    nwjs_io_url = 'https://nwjs.io/versions.json'
    try:
        versions = json.load(urllib2.urlopen(nwjs_io_url))
        nw_version = versions['stable'][1:]
    except URLError:
        print_error('Error fetching ' + nwjs_io_url + ' URL, please, set the desired NW.js version for building FFmepg using the argument -nw or --nw_version')
        sys.exit(1)

    return nw_version


def create_directory(directory):
    print 'Creating {0} directory...'.format(directory)
    try:
        os.mkdir(directory)
    except OSError:
        print_warning('{0} directory already exists, skipping...'.format(directory))


def clean_output_directory():
    print_info('Cleaning output directory...')
    shutil.rmtree(PATH_OUT, ignore_errors=True)


def setup_chromium_depot_tools(nw_version, isVersion = True):
    os.chdir(PATH_BUILD)
    if not os.path.isdir(os.path.join(PATH_DEPOT_TOOLS, '.git')):
        print_info('Cloning Chromium depot tools in {0}...'.format(os.getcwd()))
        os.system('git clone --depth=1 https://chromium.googlesource.com/chromium/tools/depot_tools.git')

    sys.path.append(PATH_DEPOT_TOOLS)
    # fix for gclient not found, seems like sys.path.append does not work but
    # path is added
    os.environ["PATH"] += os.pathsep + PATH_DEPOT_TOOLS
    if platform.system() == 'Windows' or 'CYGWIN_NT' in platform.system():
        os.environ["DEPOT_TOOLS_WIN_TOOLCHAIN"] = '0'
        os.environ["GYP_MSVS_VERSION"] = '2017'

    print_info('Creating .gclient file...')
    if(isVersion):
      subprocess.check_call('gclient config --unmanaged --name=src https://github.com/nwjs/chromium.src.git@tags/nw-v{0}'.format(nw_version), shell=True)
    else:
      subprocess.check_call('gclient config --unmanaged --name=src https://github.com/nwjs/chromium.src.git@tree/{0}'.format(nw_version), shell=True)


def clone_chromium_source_code(nw_version, isVersion = True):
    os.chdir(PATH_BUILD)
    print_info('Cloning Chromium source code for nw-{0} in {1}'.format(nw_version, os.getcwd()))
    if isVersion:
      os.system('git clone --depth=1 -b nw-v{0} --single-branch {1} src'.format(nw_version, 'https://github.com/nwjs/chromium.src.git'))
    else:
      os.system('git clone --depth=1 -b {0} --single-branch {1} src'.format(nw_version, 'https://github.com/nwjs/chromium.src.git'))


def reset_chromium_src_to_nw_version(nw_version, isVersion = True):
    os.chdir(PATH_SRC)
    if isVersion:
      print_info('Hard source code reset to nw {0} specified version'.format(nw_version))
      os.system('git reset --hard tags/nw-v{0}'.format(nw_version))
    else:
      os.system('git reset --hard')


def get_min_deps(deps_str):
    # deps
    deps_list = {
      'gyp': {
          'reg': ur"gyp.git.+@'.+'(.+)'",
          'repo': '/external/gyp.git',
          'path': 'src/tools/gyp',
          'opts': re.IGNORECASE
      },
      'patched-yasm': {
          'reg': ur"patched-yasm.git.+@'.+'(.+)'",
          'repo': '/chromium/deps/yasm/patched-yasm.git',
          'path': 'src/third_party/yasm/source/patched-yasm',
          'opts': re.IGNORECASE
      },
      'ffmpeg': {
          'reg': ur"ffmpeg.git.+@'.+'(.+)'",
          'repo': '/chromium/third_party/ffmpeg',
          'path': 'src/third_party/ffmpeg',
          'opts': re.IGNORECASE
      },
      'angle': {
          'reg': ur"angle_revision':\s*'(.+)'",
          'repo': '/angle/angle.git',
          'path': 'src/third_party/angle',
          'opts': re.IGNORECASE
      },
      'android_tools': {
          'reg': ur"android_tools.git'.*'(.+)'",
          'repo': '/android_tools.git',
          'path': 'src/third_party/android_tools',
          'opts': re.IGNORECASE
      },
      'nasm': {
          'reg': ur"nasm.git'.*?'(.{40})'",
          'repo': '/chromium/deps/nasm.git',
          'path': 'src/third_party/nasm',
          'opts':  re.MULTILINE | re.IGNORECASE | re.DOTALL
      },
      'xz': {
          'reg': ur"xz.git.+@'.+'(.+)'",
          'repo': '/chromium/deps/xz.git',
          'path': 'src/chrome/installer/mac/third_party/xz/xz',
          'opts': re.IGNORECASE
      },
      'libcxx': {
          'reg': ur"libcxx_revision.*\"(.+)\"",
          'repo': '/chromium/llvm-project/libcxx.git',
          'path': 'src/buildtools/third_party/libc++/trunk',
          'opts': re.IGNORECASE
      },
      'libcxxabi': {
          'reg': ur"libcxxabi_revision.*\"(.+)\"",
          'repo': '/chromium/llvm-project/libcxxabi.git',
          'path': 'src/buildtools/third_party/libc++abi/trunk',
          'opts': re.IGNORECASE
      }
    }
    min_deps_list = []
    for k, v in deps_list.items():
        dep = grep_dep(v['reg'], v['repo'], v['path'], deps_str, v['opts'])
        if dep is None:
            raise Exception("`%s` is not found in DEPS" % k)
        min_deps_list.append(dep)

    # Not nice but fix for mac
    min_deps_list.append('''
      'src/tools/clang/dsymutil': {
        'packages': [
          {
            'package': 'chromium/llvm-build-tools/dsymutil',
            'version': 'kykIT8m8YzNqqLP2xFGBTuo0ZtU9lom3BwiStWleyWkC',
          }
        ],
        'condition': 'checkout_mac',
        'dep_type': 'cipd',
      },
    ''')

    return textwrap.dedent('''
    deps = {
    %s
    }
    ''') % "\n".join(min_deps_list)


def get_min_vars(deps_str):
    # vars
    regex = r"(.+?)deps\s+="
    matches = re.search(regex, deps_str, re.MULTILINE | re.IGNORECASE | re.DOTALL)
    return textwrap.dedent(matches.group(1))


def get_min_hooks():
    # hooks
    # copied from DEPS
    return textwrap.dedent('''
    hooks = [
      {
        'action': [
          'python',
          'src/build/linux/sysroot_scripts/install-sysroot.py',
          '--arch=x86'
        ],
        'pattern':
          '.',
        'name':
          'sysroot_x86',
        'condition':
          'checkout_linux and (checkout_x86 or checkout_x64)'
      },
      {
        'action': [
          'python',
          'src/build/linux/sysroot_scripts/install-sysroot.py',
          '--arch=x64'
        ],
        'pattern':
          '.',
        'name':
          'sysroot_x64',
        'condition':
          'checkout_linux and checkout_x64'
      },
      {
          'name': 'mac_toolchain',
          'pattern': '.',
          'condition': 'checkout_ios or checkout_mac',
          'action': ['python', 'src/build/mac_toolchain.py'],
      },
      {
        # Update the Windows toolchain if necessary.  Must run before 'clang' below.
        'name': 'win_toolchain',
        'pattern': '.',
        'condition': 'checkout_win',
        'action': ['python', 'src/build/vs_toolchain.py', 'update', '--force'],
      },
      {
        'action': [
          'python',
          'src/tools/clang/scripts/update.py'
        ],
        'pattern':
          '.',
        'name':
          'clang'
      },
      {
        'action': [
          'python',
          'src/chrome/android/profiles/update_afdo_profile.py'
        ],
        'pattern': '.',
        'condition': 'checkout_android or checkout_linux',
        'name': 'Fetch Android AFDO profile'
      },
      {
        'action': [
          'download_from_google_storage',
          '--no_resume',
          '--no_auth',
          '--bucket',
          'chromium-gn',
          '-s',
          'src/buildtools/win/gn.exe.sha1'
        ],
        'pattern':
          '.',
        'name':
          'gn_win',
        'condition':
          'host_os == "win"'
      },
      {
        'action': [
          'download_from_google_storage',
          '--no_resume',
          '--no_auth',
          '--bucket',
          'chromium-gn',
          '-s',
          'src/buildtools/mac/gn.sha1'
        ],
        'pattern':
          '.',
        'name':
          'gn_mac',
        'condition':
          'host_os == "mac"'
      },
      {
        'action': [
          'download_from_google_storage',
          '--no_resume',
          '--no_auth',
          '--bucket',
          'chromium-gn',
          '-s',
          'src/buildtools/linux64/gn.sha1'
        ],
        'pattern':
          '.',
        'name':
          'gn_linux64',
        'condition':
          'host_os == "linux"'
      },
      {
        'name': 'clang_format_mac',
        'pattern': '.',
        'condition': 'host_os == "mac"',
        'action': [ 'python',
                    'src/third_party/depot_tools/download_from_google_storage.py',
                    '--no_resume',
                    '--no_auth',
                    '--bucket', 'chromium-clang-format',
                    '-s', 'src/buildtools/mac/clang-format.sha1',
        ],
      },
        # Pull rc binaries using checked-in hashes.
      {
        'name': 'rc_win',
        'pattern': '.',
        'condition': 'checkout_win and host_os == "win"',
        'action': [ 'python',
                'src/third_party/depot_tools/download_from_google_storage.py',
                '--no_resume',
                '--no_auth',
                '--bucket', 'chromium-browser-clang/rc',
                '-s', 'src/build/toolchain/win/rc/win/rc.exe.sha1',
        ],
      },
      {
        'name': 'rc_mac',
        'pattern': '.',
        'condition': 'checkout_win and host_os == "mac"',
        'action': [ 'python',
                    'src/third_party/depot_tools/download_from_google_storage.py',
                    '--no_resume',
                    '--no_auth',
                    '--bucket', 'chromium-browser-clang/rc',
                    '-s', 'src/build/toolchain/win/rc/mac/rc.sha1',
        ],
      },
      {
        'name': 'lastchange',
        'pattern': '.',
        'action': ['python', 'src/build/util/lastchange.py', '-o', 'src/build/util/LASTCHANGE'],
      },
      {
        'name': 'gpu_lists_version',
        'pattern': '.',
        'action': ['python', 'src/build/util/lastchange.py', '-m', 'GPU_LISTS_VERSION', '--revision-id-only', '--header', 'src/gpu/config/gpu_lists_version.h'],
      },
    ]
    recursedeps = [
      'src/buildtools'
    ]
    ''')


def install_build_deps():
    os.chdir(PATH_SRC_BUILD)
    if platform.system() == 'Linux' and not os.path.isfile('buid_deps.ok'):
        print_info('Installing build dependencies...')
        os.system('./install-build-deps.sh --no-prompt --no-nacl --no-chromeos-fonts --no-syms')
        with io.FileIO('buid_deps.ok', 'w') as file:
            file.write('Build dependencies already installed')


def gclient_sync():
    os.chdir(PATH_SRC)
    print_info('Syncing with gclient...')
    os.system('gclient sync --no-history')


def build(target_cpu):
    os.chdir(PATH_SRC)
    print_info('Generating ninja files...')
    subprocess.check_call('gn gen //out/nw "--args=is_debug=false is_component_ffmpeg=true target_cpu=\\\"%s\\\" is_official_build=true ffmpeg_branding=\\\"Chrome\\\""' % target_cpu, shell=True)
    print_info('Starting ninja for building ffmpeg...')
    subprocess.check_call('ninja -C out/nw ffmpeg', shell=True)


def delete_file(file_name):
    if os.path.exists(file_name):
        try:
            os.remove(file_name)
        except OSError as e:
            print_error("%s - %s." % (e.filename, e.strerror))


def generate_build_and_deps_files():
    os.chdir(PATH_SRC)
    print_info('Cleaning previous DEPS and BUILD.gn backup files...')

    delete_file("DEPS.bak")
    delete_file("BUILD.gn.bak")

    with open('DEPS', 'r') as f:
        deps_str = f.read()

    print_info('Backing up and overwriting DEPS...')
    shutil.move('DEPS', 'DEPS.bak')
    with open('DEPS', 'w') as f:
        f.write("%s\n%s\n%s" % (get_min_vars(deps_str), get_min_deps(deps_str), get_min_hooks()))

    print_info('Backing up and overwriting BUILD.gn...')
    shutil.move('BUILD.gn', 'BUILD.gn.bak')

    BUILD_gn = textwrap.dedent('''
    group("dummy") {
      deps = [
        "//third_party/ffmpeg"
      ]
    }
    ''')

    with open('BUILD.gn', 'w') as f:
        f.write(BUILD_gn)


def zip_release_output_library(nw_version, platform_release_name, target_arch, out_library_path, output_release_path):
    create_directory(output_release_path)
    print_info('Creating release zip...')
    if os.path.isfile(out_library_path):
        with zipfile.ZipFile(os.path.join(output_release_path, '{0}-{1}-{2}{3}.zip'.format(nw_version, platform_release_name, target_arch, '')), 'w', zipfile.ZIP_DEFLATED) as release_zip:
            release_zip.write(out_library_path, os.path.basename(out_library_path))
            release_zip.close()
    else:
        print_warning('There is no release file library in {0}...'.format(out_library_path))


#following from Python cookbook, #475186
def has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False


def print_message(color, message_type, message):
    if has_colours(sys.stdout):
        print (color + message_type + COLOR_NORMAL + message)
    elif get_host_platform() == "win":
        if color == COLOR_OK:
            windows_color = COLOR_OK_WINDOWS
        elif color == COLOR_ERROR:
            windows_color = COLOR_ERROR_WINDOWS
        elif color == COLOR_INFO:
            windows_color = COLOR_INFO_WINDOWS
        elif color == COLOR_WARNING:
            windows_color = COLOR_WARNING_WINDOWS
        print_windows_message (windows_color, message_type + message)
    else:
      print (message_type + message)


def print_windows_message(colour, message):
    import ctypes
    ctypes.windll.Kernel32.GetStdHandle.restype = ctypes.c_ulong
    h = ctypes.windll.Kernel32.GetStdHandle(ctypes.c_ulong(0xfffffff5))
    def colorize(colour):
        ctypes.windll.Kernel32.SetConsoleTextAttribute(h, colour)
    colorize(colour)
    print message
    colorize(COLOR_NORMAL_WINDOWS)


def print_ok(message):
    print_message (COLOR_OK, message, '')


def print_error(message):
    print_message (COLOR_ERROR, 'ERROR: ', message)


def print_info(message):
    print_message (COLOR_INFO, 'INFO: ', message)


def print_warning(message):
    print_message (COLOR_WARNING, 'WARNING: ', message)


if __name__ == '__main__':
    sys.exit(main())
