#!/bin/bash

sudo apt update
sudo apt install -y jq bc

# Store versions in variables
NW=$(curl -s https://nwjs.io/versions | jq -r ".latest")
FF=v$(curl -s https://api.github.com/repos/nwjs-ffmpeg-prebuilt/nwjs-ffmpeg-prebuilt/releases | jq -r ".[0].tag_name")

NW=${NW:1}
FF=${FF:1}

# If NW.js version is greater than FFmpeg version, exit with error
FLAG=$(echo "$NW > $FF" | bc -l)

if [ $FLAG == 0 ]; then
    exit 1;
else
    exit 0;
fi
