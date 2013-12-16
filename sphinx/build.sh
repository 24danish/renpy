#!/bin/sh

SPHINX="$(dirname $(python -c "import os;print(os.path.realpath('$0'))"))"
cd $SPHINX

../renpy.sh . || exit 1

sphinx-build -a source ../doc || exit 1

python checks.py

