#!/bin/bash

if [ "$IMAGE" == "Visual Studio 2019" ]; then
  ICON="assets/icons/icon.ico"
elif [ "$IMAGE" == "macOS" ]; then
  ICON="assets/icons/icon.png"
elif [ "$IMAGE" == "Ubuntu" ]; then
  ICON="assets/icons/icon.pngg"
fi

flet pack main.py --name fletsheet --icon $ICON --product-name fletsheet --product-version "0.0.1" --copyright "MIT License"
