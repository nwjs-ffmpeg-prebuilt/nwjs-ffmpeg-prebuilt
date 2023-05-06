#!/bin/bash

# Store versions in variables
NW=$(curl -s https://nwjs.io/versions | jq -r ".latest")
FF=v$(curl -s https://api.github.com/repos/nwjs-ffmpeg-prebuilt/nwjs-ffmpeg-prebuilt/releases | jq -r ".[0].tag_name")

NW=${NW:1}
FF=${FF:1}

if [ "$(echo -e "${NW}\n${FF}" | sort -V | head -n1)" == "$NW" ]; then
    exit 1
else
    exit 0
fi
