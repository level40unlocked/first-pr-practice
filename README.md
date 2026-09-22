# first-pr-practice

A tiny practice project for learning the GitHub first-PR workflow.

## What's here

- `greet.py` - a small function that returns a greeting for a given name.
- `animate_image.py` - turns a still 2D image into a short video with a
  simple pan/zoom (Ken Burns) animation.
- `lipsync_video.py` - turns a 2D character into a short "talking" video by
  swapping mouth shapes in sync with the volume of an audio track.

## Usage

```bash
python greet.py
```

This will print a greeting to the console.

### Animating a 2D image

Install the dependencies once:

```bash
pip install -r requirements.txt
```

Then generate an animated video from any image:

```bash
python animate_image.py path/to/image.jpg -o output.mp4 --effect zoom_in --duration 4 --fps 30
```

Available `--effect` options: `zoom_in`, `zoom_out`, `pan_left`, `pan_right`,
`pan_up`, `pan_down`. Use `--zoom` to control how strong the effect is (must
be greater than `1.0`), and `--no-ease` to disable the ease-in-out timing.

### Making a 2D character talk (lip-sync)

`lipsync_video.py` is a "phase 1", rule-based lip-sync: it has no AI model,
it just switches between a few drawn mouth shapes (`closed`, `mid`, `open`)
based on how loud the audio is at each moment.

Try it immediately with no assets of your own — it generates a placeholder
character and a placeholder speech-like audio track automatically:

```bash
pip install -r requirements.txt
python lipsync_video.py -o talking.mp4
```

To use your own character art and audio, pass a character folder and an
audio file:

```bash
python lipsync_video.py -c path/to/character_dir -a path/to/speech.mp3 -o talking.mp4
```

The character folder must contain four PNGs, all the same canvas size:

- `base.png` - the character with a neutral/empty mouth area
- `mouth_closed.png`, `mouth_mid.png`, `mouth_open.png` - transparent
  overlays with just the mouth drawn in each shape, positioned exactly
  where it should appear on `base.png`

## Running

Just run the script directly with Python 3.

## Tests

```bash
python -m unittest test_greet.py
python -m unittest test_animate_image.py
python -m unittest test_lipsync_video.py
```
