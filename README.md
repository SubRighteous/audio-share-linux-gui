# Audio-Share GUI for Linux


A simple PyQt6-based GUI for [mkckr0/audio-share](https://github.com/mkckr0/audio-share), designed to make sharing audio on Linux easier — with the goal of matching the features available on the official Windows version. 

This project does not include the main audio-share command-line tool (as-cmd) for Linux.
You must download [audio-share-server-cmd-linux](https://github.com/mkckr0/audio-share/releases) separately and extract only "as-cmd" in the root directory of this project for the app to function properly.

This is not an official Audio Share application.
It's an independent, personal project created to improve the my experience of using audio-share on Linux.
There is no affiliation or support from the original developers of [mkckr0/audio-share](https://github.com/mkckr0/audio-share).

This app executes the terminal commands required to launch and manage an audio-share server. Also the icon used in this project is from the audio-share project by [mkckr0](https://github.com/mkckr0).
All rights to the original artwork belong to its respective creator.

## Screenshots

![app_screenshot_01](https://github.com/user-attachments/assets/021cc3be-b3c9-4211-8040-631be217dcd7)
![app_screenshot_02](https://github.com/user-attachments/assets/6d770ab4-1fc8-4995-b316-f791cd1a9c5c)

## Requirements
* A PC with Linux
* Linux with PipeWire
* Python 3 (tested on 3.13)

## Install/Run from Source

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

(Optional) Make an python virutal enviroment
```bash
  python -m venv
```
Activate the python venv
```bash
  source venv/bin/activate
```
Install dependencies

```bash
  pip install -r requirements.txt
```

Start the app (with python venv)

```bash
  <venv path>/bin/python <app path>/AudioShare_LinuxGUI/src/main.py
```

Start the app (without python venv)
```
  <python install path>/bin/python <app path>/AudioShare_LinuxGUI/src/main.py
```
## Used Third-party Libraries

PyQt6\
Used to build the graphical user interface (GUI).\
License: GPL v3 or commercial license [(details)](https://www.riverbankcomputing.com/commercial/license-faq)

Bootstrap\
Used for styling the embedded web UI components.\
License: MIT [(details)](https://github.com/twbs/bootstrap/blob/main/LICENSE)

Audio-Share
Core functionality provided by the as-cmd tool.
License: Apache-2.0 license [(details)](https://github.com/mkckr0/audio-share/blob/main/LICENSE)
