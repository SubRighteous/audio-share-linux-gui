#!/usr/bin/env bash

current_dir=$(pwd)

desktop_file_path="$current_dir/Audio-Share.desktop"
build_exec_path="$current_dir/main.dist/main.bin"  # Or the built binary
app_icon_path="$current_dir/main.dist/assets/icon.png"  # Optional

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
echo -e "\n"
while true; do
    echo -e ""
    read -p "Do you want to create the .desktop file? (y/n) " yn
    case $yn in
        [Yy]* ) echo -e "\nCreating .desktop file at $desktop_file_path";
                cat > "$desktop_file_path" <<EOL
[Desktop Entry]
Type=Application
Name=AudioShare
Exec=$build_exec_path
Icon=$app_icon_path
Terminal=false
Categories=Utility;
EOL

            chmod +x "$desktop_file_path"
            break;;
        [Nn]* ) echo -e "\nExiting..."; exit;;
        * ) echo "Invalid input. Please answer yes or no.";;
    esac
done
echo -e "\n"
while true; do
    read -p "Do you want to move the .desktop file to ($HOME/.local/share/applications)? (y/n) " yn
    case $yn in
        [Yy]* ) mv $desktop_file_path "$HOME/.local/share/applications/Audio-Share.desktop";
                echo -e "\nExiting..."
                break;;
        [Nn]* ) echo -e "\nExiting..."; exit;;
        * ) echo "Invalid input. Please answer yes or no.";;
    esac
done