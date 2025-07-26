#!/bin/bash -e
_chromium=$1
# Use rg for macOS
_commit=$(curl -sL https://raw.githubusercontent.com/chromium/chromium/refs/tags/${_chromium}/DEPS | rg -oP "'ffmpeg_revision': '\K[0-9a-f]{40}'" | tr -d \')
git init
git remote add origin https://chromium.googlesource.com/chromium/third_party/ffmpeg
git fetch --depth=1 origin $_commit
git checkout $_commit
