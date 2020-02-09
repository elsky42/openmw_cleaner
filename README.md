# openmw_cleaner
Runs tes3cmd clean on the mods that require it.

This is a small script that finds the installed mods and cleans the ones that require
cleaning based on the information found on [modding-openmw](https://modding-openmw.com/) lists.

## Installation

You need `Python` and [`tes3cmd`](https://modding-openmw.com/mods/tes3cmd/) installed. Download the script `cleaner.py` on the computer where the mods to clean are.

## Usage

The script needs to know where the `openmw.cfg` file is and the `modding-openwm.com` list to check. Optionally
you can pass the path to `tes3cmd`.

For instance:

```
$ python /cleaner.py -c 'C:\Users\elsky\Documents\My Games\OpenMW\openmw.cfg' -u https://modding-openmw.com/lists/expanded-vanilla/ -t C:\Users\elsky\Downloads\morrowind\tes3cmd.exe
```