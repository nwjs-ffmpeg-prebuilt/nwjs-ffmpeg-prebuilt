const { spawn } = require('child_process');
const { promisify } = require('util');
const fs = require('fs-extra');
const path = require('path');
const got = require('got');
const program = require('commander');

program
    .option('-a, --arch [arch]', 'Target architecture, ia32, x64', 'x64')
    .option('-v, --version [version]', 'Build ffmpeg for the specified Nw.js version or Branche', false)
    .option('-c, --clean', 'Clean the workspace, removes downloaded source code');

program.parse(process.argv);

function execAsync(code, ...a) {
    return new Promise((resolve) => {
        const proc = spawn(code, a, { stdio: 'inherit' });
        proc.addListener('exit', resolve);
    });
}

async function main() {

    const pkg = await got('https://nwjs.io/versions.json').json();
    const nwVersion = program.version || pkg.stable;
    const version = pkg.versions.find(e => e.version === nwVersion);
    const chromiumVersion = version.components.chromium;
    console.log(`Building Chromium ${chromiumVersion} (${nwVersion}).`)
    const isX86 = false;
    if(program.clean) {
        // TODO: implement clean
    }
    await fs.ensureDir('./build');
    process.chdir('./build');
    if (!(await fs.pathExists('./depot_tools'))) {
        await execAsync('git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git');
    }
    process.env.PATH = `${process.env.PATH}:${path.resolve('./depot_tools')}`;
    if (process.platform === 'win32') {
        process.env.DEPOT_TOOLS_WIN_TOOLCHAIN = '1';
    }
    await fs.ensureDir('./chromium')
    process.chdir('./chromium')
    if (!(await fs.pathExists('./src'))) {
        await execAsync(`fetch`, `--nohooks`, `--no-history`, `chromium`);
    }

    process.chdir('./src')

    if (process.platform === 'linux') {
        await execAsync(`./build/install-build-deps.sh`, `--no-prompt`, `--no-nacl`, `--no-chromeos-fonts`, `--no-syms`);
    }

    console.log(`Fetching ${chromiumVersion}`)
    await execAsync(`git`, `fetch`, `origin`, chromiumVersion, '--no-tags');

    console.log(`Checking out ${chromiumVersion}`)
    await execAsync(`git`, `checkout`, `${chromiumVersion}`);

    console.log(`Gclient Sync`)
    await execAsync('gclient', 'sync', '--no-history');

    if (program.arch === 'x86') {
        await execAsync('gn gen out/Default "--args=is_debug=false is_component_ffmpeg=true target_cpu=\"x64\" is_official_build=true ffmpeg_branding=\"Chrome\""');
    } else {
        await execAsync('gn gen out/Default "--args=is_debug=false is_component_ffmpeg=true target_cpu=\"x64\" is_official_build=true ffmpeg_branding=\"Chrome\""');
    }
    if (process.platform === 'darwin') {
        await execAsync('autoninja -C out\Default libffmpeg.so')
    } else if (process.platform === 'win32') {
        await execAsync('autoninja -C out\Default ffmpeg.dll')
    }else if (process.platform === 'linux') {
        await execAsync('autoninja -C out\Default libffmpeg.so')
    }
    
    //const zip = new JSZip();
    //zip.file("Hello.txt", );

}

main().catch((e) => {
    console.error(e);
});