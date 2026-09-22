# first-pr-practice

A tiny practice project for learning the GitHub first-PR workflow.

## What's here

- `greet.py` - a small function that returns a greeting for a given name.
- `animate_image.py` - turns a still 2D image into a short video with a
  simple pan/zoom (Ken Burns) animation.
- `lipsync_video.py` - turns a 2D character into a short "talking" video by
  swapping mouth shapes in sync with the volume of an audio track.
- `pose_video.py` - turns a small set of drawn poses (e.g. a 2-pose walk
  cycle) into a short video by cycling through them on a fixed cadence.

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

`lipsync_video.py` is a rule-based lip-sync: it has no AI model. It reads
three drawn mouth shapes (`closed`, `mid`, `open`) and picks one per frame
based on how loud the audio is at that moment. Loudness is smoothed with an
envelope follower (mouth snaps open quickly, closes more gradually) before
picking the shape, so state changes land at natural moments in the speech
instead of chattering on raw, jittery amplitude. Mouth shapes are switched,
not cross-faded — blending two differently-shaped overlays would show both
shapes translucently at once.

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

`assets/sample_character/` is a real example built from an AI-generated 2D
portrait: the mouth line in the original artwork was located, patched out
with a soft skin-colored patch to make `base.png`, and the three mouth
overlays were hand-drawn at that same position to match the art style. Try
it with:

```bash
python lipsync_video.py -c assets/sample_character -a path/to/speech.mp3 -o talking.mp4
```

### Making a 2D character move (simple pose cycling)

`pose_video.py` is for movement that doesn't need to look smooth or
rigged — just enough to read as "this character is moving on screen," like
a stiff walk cycle. There's no rotation, no rigging, no interpolation: it
just cycles through a small set of complete, already-drawn poses (the same
trick as `lipsync_video.py`'s mouth-shape switching, applied to whole-body
poses).

Try it immediately with a built-in placeholder 2-pose walk cycle:

```bash
python pose_video.py -o walking.mp4
```

To use your own poses, pass a folder of `pose_*.png` files (all the same
size, cycled in sorted filename order, e.g. `pose_01.png`, `pose_02.png`):

```bash
python pose_video.py -p path/to/pose_dir -o walking.mp4 --step-frames 4
```

`--step-frames` controls how many frames each pose holds before switching
to the next — higher is slower/choppier, lower is faster. Pass `-a` to mux
in an audio track (also sets the video's duration to match).

## Running

Just run the script directly with Python 3.

## Tests

```bash
python -m unittest test_greet.py
python -m unittest test_animate_image.py
python -m unittest test_lipsync_video.py
python -m unittest test_pose_video.py
```
