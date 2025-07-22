# PSP-God-Eater-2-English-Patch
### Extension of RedArtz's Translation Project. <br>
Polishing translations, creating injected translated textures, translating voice overs.

The tools we use is created by Gil Unx.<br>
https://github.com/gil-unx <br>
https://youtu.be/Hngv-p7bqVA?si=7gxhLi-wX4KudiDj

And from what i recognize, some of the txt files are from ColdBird's old project. <br>
https://github.com/MrColdbird <br>
https://github.com/MrColdbird/God-Eater-2-Translation-Project

Some stuff is also taught to my by Yamato Nagisaki <br>
https://github.com/nachotacos69

## How to use
### On Windows Desktop
Make sure you have Python installed.
https://www.python.org/downloads/windows/

Modify `INJECTOR.cfg` using notepad so it can find the files needed to patch

Open **Command Prompt** and run the following commands <br>
`pip install pillow` <br>
`pip install pypng` <br>
after that everytime you open i suggest to run this command <br>
`cd /d (directory of the translation files)` <br>
once it is set to the directory of the files run this command <br>
`python (\Directory of translation files\SCRIPT_INJECTOR.py)` <br>
after that wait for it to be finished.

be informed that the game wouldn't work if the DLC and the iso patches don't match so you have to move the new DLC to /PSP/GAME/.

Some parts can only be translated using HEX Editor like the texts in the terminal "Deposit Items" "Withdraw Items"

### Termux setup on android

```pkg update &&
pkg upgrade
pkg install python
pkg install libjpeg-turbo
pip install pillow
pip install pypng```