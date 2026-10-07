# Security Policy

## Security maintainer

[@zkrige](https://github.com/zkrige) (Zayin Krige) is the security maintainer for this project and triages every report.

## Supported versions

Only the latest release receives security fixes. Older builds are not rebuilt.

## Reporting a vulnerability

Report privately through GitHub: [Report a vulnerability](https://github.com/nwjs-ffmpeg-prebuilt/nwjs-ffmpeg-prebuilt/security/advisories/new). Do not open a public issue.

In scope:

- The build scripts (`build.sh`, `build.js`) and GitHub Actions workflows
- The published release binaries, including build flags and the codec set they enable

Out of scope here, report upstream:

- Vulnerabilities in FFmpeg source code: ffmpeg-security@ffmpeg.org (see https://ffmpeg.org/security.html)
- Vulnerabilities in NW.js or Chromium: https://github.com/nwjs/nw.js

When an upstream fix affects these binaries, it ships in the next release, and the advisory names the release that contains it.
