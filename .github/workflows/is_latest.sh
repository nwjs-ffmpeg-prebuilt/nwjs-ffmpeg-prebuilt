#!/bin/bash

# Check if the script is triggered by workflow_dispatch
if [ "$1" == "workflow_dispatch" ]; then
    echo "Manual build triggered, skipping version check."
    exit 0
fi


# Store versions in variables
NW=$(curl -s https://nwjs.io/versions.json | jq -r ".latest")
FF=v$(curl -s https://api.github.com/repos/nwjs-ffmpeg-prebuilt/nwjs-ffmpeg-prebuilt/releases | jq -r ".[0].tag_name")

# Remove v from both strings
NW=${NW:1}
FF=${FF:1}


# Split string at . into arrays
IFS='.' read -ra NW_VER <<< "$NW"
IFS='.' read -ra FF_VER <<< "$FF"

# If the major, minor or patch version of NW.js
# is larger than FFmpeg's latest released version,
# then trigger a release.

if [ "${NW_VER[0]}" -gt "${FF_VER[0]}" ]; then
    echo "NW.js version $NW is greater than FFmpeg's latest release $FF."
    exit 0
fi

if [ "${NW_VER[1]}" -gt "${FF_VER[1]}" ]; then
    echo "NW.js version $NW is greater than FFmpeg's latest release $FF."
    exit 0
fi

if [ "${NW_VER[2]}" -gt "${FF_VER[2]}" ]; then
    echo "NW.js version $NW is greater than FFmpeg's latest release $FF."
    exit 0
fi

exit 1
