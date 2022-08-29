#!/bin/bash
find ./ -name "*.svg" -exec inkscape -z -w 1024 -h 1024 {} -o {}.png \;
ffmpeg -y -i %1d.svg.png -vf palettegen=reserve_transparent=1 palette.png
ffmpeg -y -framerate 5 -i %1d.svg.png -i palette.png -lavfi paletteuse=alpha_threshold=1 -gifflags -offsetting out.gif
