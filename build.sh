#!/usr/bin/env bash

current_dir=$(pwd)
venv_dir="$current_dir/.venv"

if test -d "$venv_dir"; then
    echo "Python venv exists."

    sudo .venv/bin/nuitka --follow-imports --enable-plugin=pyqt6 \
        --include-data-dir=src/frontend=frontend \
        --include-data-dir=src/assets=assets \
        --include-data-files=src/as-cmd=as-cmd \
        --standalone src/main.py
else
    echo -e "\nMissing Python venv at $venv_dir"
    echo -e "\nPlease follow the following steps to build the venv"

    echo -e "\t1. Create the python venv with the name \".venv\" ( python -m venv .venv )"
    echo -e "\t2. Activate the python venv ( source .venv/bin/activate )"
    echo -e "\t3. Install dependencies ( pip install -r requirements.txt )"

    echo -e "\nAfter installing dependencies, make sure \"as-cmd\" is included in the \"src\" folder"
    echo -e "\nIt can be downloaded at \"https://github.com/mkckr0/audio-share/releases\"\nmake sure download \"audio-share-server-cmd-linux.tar.gz\" and only extract the \"as-cmd\" file\n"
fi
