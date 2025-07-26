FFMPEG_VERSION=$(strings extracted/linux/build/out/libffmpeg.so | grep -Eo 'ffmpeg version [^ ]+' | head -n 1)
echo "FFMPEG_VERSION=${FFMPEG_VERSION}" >> $GITHUB_ENV
echo "## Release Notes" > release-notes.md
echo "- NW.js version: $NW" >> release-notes.md
echo "- Chromium version: $(curl -s https://nwjs.io/versions.json | jq -r .versions[0].components.chromium)" >> release-notes.md
echo "- ${FFMPEG_VERSION}" >> release-notes.md
echo "- Includes builds for Windows, macOS, and Linux" >> release-notes.md
