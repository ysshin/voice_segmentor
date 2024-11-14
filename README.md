
# voice_segmentor

A set of scripts that reads media -> detect voice from the media -> create wav for each sentences

## Scripts

### `folder_convert_media_to_wav.py`
convert all non-wav media into wav in a given folder
it uses ffmpeg internally as that's performing the best (most stable, and compatible with any)
ffmpeg uses default which is 16 bit PCM, 48Khz, 2ch

**Usage:**
```bash
python folder_convert_media_to_wav.py -f <folder name>
```
---
### `segment-media-vad-onx.py`
Reads either a single wave file or all the wave files in a specific folder, and run Voice Activity Dector (with onx option enabled) to generate a folder that has each sentences as wave file
it internally uses https://github.com/snakers4/silero-vad for Voice activity Detection

**Usage:**
For a single wave file
```bash
python segment-media-vad-onx.py <wave file>
```
For all wave file in a folder
```bash
python segment-media-vad-onx.py -f <folder>
```
