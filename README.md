# Audio-Share GUI for Linux


A simple PyQt6-based GUI for [mkckr0/audio-share](https://github.com/mkckr0/audio-share), designed to make sharing audio on Linux easier — with the goal of matching the features available on the official Windows version. 

This project does not include the main audio-share command-line tool (as-cmd) for Linux.
You must download [audio-share-server-cmd-linux](https://github.com/mkckr0/audio-share/releases) separately and extract the "as-cmd" in the root directory of this project for the app to function properly.

This is not an official Audio Share application.
It's an independent, personal project created to improve my experience using audio-share on Linux.
There is no affiliation or support from the original developers of [mkckr0/audio-share](https://github.com/mkckr0/audio-share).

This app executes the terminal commands required to launch and manage an audio-share server. The icon used in this project is also from the audio-share project by [mkckr0](https://github.com/mkckr0).
All rights to the original artwork belong to its respective creator.

## Screenshots

![app_screenshot_01](https://github.com/user-attachments/assets/4bb75056-9db3-45f0-b8b8-9307df94ae4a)
![app_screenshot_02](https://github.com/user-attachments/assets/04e6852e-6300-45d4-8eb1-8a25fdbe2a3e)

## Requirements
* A PC with Linux
* Linux with PipeWire
* Linux desktop environment with a system tray
* Python 3 (tested on 3.13)
* xcb plugin for qt
```bash
  sudo apt-get install libxcb-cursor0 libxcb-render-util0 libxcb-image0 libxcb-keysyms1 libxcb-icccm4
```
* as-cmd (0.34 or later) from [mkckr0/audio-share](https://github.com/mkckr0/audio-share/releases)

## Run from Source

Clone the project

```bash
git clone https://github.com/SubRighteous/audio-share-linux-gui
```

Go to the project directory

```bash
cd audio-share-linux-gui-main
```

Download the latest version of as-cmd from [https://github.com/mkckr0/audio-share/releases](https://github.com/mkckr0/audio-share/releases)
```bash
wget https://github.com/mkckr0/audio-share/releases/download/v0.3.4/audio-share-server-cmd-linux.tar.gz
```

Extract to the "src" folder
```bash
tar -xf audio-share-server-cmd-linux.tar.gz --strip-components 2
```

Move "as-cmd" to the "src" folder
```bash
mv as-cmd ./src/as-cmd
```

(Optional) Create a Python virtual environment
```bash
python -m venv .venv
```
Activate the Python virtual environment
```bash
source .venv/bin/activate
```
Install dependencies

```bash
pip install -r requirements.txt
```

Start the app (using the Python virtual environment)

```bash
.venv/bin/python ./src/main.py
```

Start the app (without a virtual environment)
```
<python install path>/bin/python ./src/main.py
```
## Build from Source
Clone the project

```bash
git clone https://github.com/SubRighteous/audio-share-linux-gui
```

For instructions, follow the [Building the project](https://github.com/SubRighteous/audio-share-linux-gui/wiki/Build-from-Source) guide on the wiki.

## Used Third-party Libraries

PyQt6\
Used to build the graphical user interface (GUI).\
License: GPL v3 or commercial license [(details)](https://www.riverbankcomputing.com/commercial/license-faq)

Bootstrap\
Used for styling the embedded web UI components.\
License: MIT [(details)](https://github.com/twbs/bootstrap/blob/main/LICENSE)

Audio-Share\
Core functionality provided by the as-cmd tool.\
License: Apache-2.0 license [(details)](https://github.com/mkckr0/audio-share/blob/main/LICENSE)
