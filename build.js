#!/usr/bin/env node
const { spawn } = require('child_process');
const fs = require('fs-extra');
const path = require('path');
const got = require('got');
const program = require('commander');
const yazl = require("yazl");
const outDir = path.join(process.cwd(), 'build', 'out');
program
    .option('-a, --arch [arch]', 'Target architecture, ia32, x64', 'x64')
    .option('-v, --version [version]', 'Build ffmpeg for the specified Nw.js version or Branch', false)
    .option('-c, --clean', 'Clean the workspace, removes downloaded source code');

program.parse(process.argv);

function execAsync(code, ...a) {
    return new Promise((resolve) => {
        const proc = spawn(code, a, {
            stdio: 'inherit',
            shell: true,
            env: {
                ...process.env
            } 
        });
        proc.addListener('exit', resolve);
    });
}

async function main() {
    const pkg = await got('https://nwjs.io/versions.json').json();
    const nwVersion = program.version || pkg['stable'];
    const version = pkg.versions.find(e => e.version === nwVersion);
    const chromiumVersion = version['components']['chromium'];
    console.log(`Building Chromium ${chromiumVersion} (${nwVersion}).`);
    if(program.clean) {
        // TODO: implement clean
    }
    await fs.ensureDir(outDir);
    await fs.ensureDir('./build');
    process.chdir('./build');
    if (!(await fs.pathExists('./depot_tools'))) {
        await execAsync('git', 'clone', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git');
    }
    if (process.platform === 'win32') {
        process.env.DEPOT_TOOLS_WIN_TOOLCHAIN = '0';
        process.env.PATH = `${process.env.PATH};${path.resolve('./depot_tools')}`;
    }else {
        process.env.PATH = `${process.env.PATH}:${path.resolve('./depot_tools')}`;
    }
    await fs.ensureDir('./chromium');
    process.chdir('./chromium');
    const hasSrc = await fs.pathExists('./src');
    console.log(`Clone chromium.src`);
    if (!hasSrc) {
        const gclient = `
solutions = [
    { "name"        : 'src',
        "url"         : 'https://chromium.googlesource.com/chromium/src.git',
        "deps_file"   : 'DEPS',
        "managed"     : False,
        "custom_deps" : {

        },
        "custom_vars": {},
    },
]
        `.trim()
        await fs.writeFile('.gclient', gclient);
        await execAsync('git', 'clone', 'https://chromium.googlesource.com/chromium/src.git', '--branch', chromiumVersion, '--single-branch', '--depth', 1);
    }
    process.chdir('./src');
    if(hasSrc) {
        await execAsync('git', 'fetch', 'https://chromium.googlesource.com/chromium/src.git', `+refs/tags/${chromiumVersion}`, '--depth', 1);
    }

    await execAsync('git', 'reset', '--hard', `tags/${chromiumVersion}`);

    if (process.platform === 'linux') {
        await execAsync(`./build/install-build-deps.sh`, `--no-prompt`, `--no-nacl`, `--no-chromeos-fonts`, `--no-syms`);
    }
    
    await execAsync('gclient', 'sync', '--with_branch_heads');
    if (program.arch === 'ia32') {
        await execAsync('gn', 'gen', 'out/Default', '--args="is_debug=false is_component_ffmpeg=true is_official_build=true target_cpu=\\"x86\\" ffmpeg_branding=\\"Chrome\\""');
    } else {
        await execAsync('gn', 'gen', 'out/Default', '--args="is_debug=false is_component_ffmpeg=true is_official_build=true target_cpu=\\"x64\\" ffmpeg_branding=\\"Chrome\\""');
    }
    let libName = null;
    let zipName = null;
    if (process.platform === 'darwin') {
        libName = 'libffmpeg.dylib';
        zipName = `${nwVersion}-osx-${program.arch}.zip`;
    } else if (process.platform === 'win32') {
        libName = 'ffmpeg.dll';
        zipName = `${nwVersion}-win-${program.arch}.zip`;
    }else if (process.platform === 'linux') {
        libName = 'libffmpeg.so';
        zipName = `${nwVersion}-linux-${program.arch}.zip`;
    }
    await execAsync('autoninja', '-C', 'out/Default', libName)
    zipName=zipName.slice(1);
    const zipfile = new yazl.ZipFile();
    zipfile.addFile(`out/Default/${libName}`, libName);
    
    zipfile.outputStream.pipe(fs.createWriteStream(path.resolve(outDir, zipName))).on("close", () => {
        console.log(zipName);
    });
    zipfile.end();
}

main().catch((e) => {
    console.error(e);
});