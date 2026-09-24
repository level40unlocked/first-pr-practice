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
- `body_wiggle.py` - animates a single 2D character image with a simple
  whole-body bounce/rock cycle, without cutting the artwork or generating
  any extra images.
- `talking_head_video.py` - like `lipsync_video.py`, but the head also
  nods/tilts independently of a static body, using a circular head layer
  that never shows a seam no matter the angle.

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

### Making a single character image wiggle (no cutting, no extra AI calls)

Cutting a real, detailed character illustration into limb pieces and
rotating them (like `pose_video.py`'s poses would need for a real walk
cycle) turns out to be fragile in practice — fingers get clipped, legs
cross, seams show at the shoulders. Generating a separate AI image per pose
avoids that but costs money and the character can drift between
generations. `body_wiggle.py` avoids both problems: it never cuts the
artwork at all. It moves the *entire* image as one rigid piece — a small
bounce/rock cycle (vertical shift + a slight tilt, pivoting near the feet)
— derived from a single source image with plain PIL rotate/paste calls.
Since nothing is ever cut apart, there's nothing that can look disjointed.
It works best on art with a flat, uniform background color, which fills in
whatever edge the shift/rotation exposes.

```bash
python body_wiggle.py path/to/character.png -o wiggle.mp4
```

`--amplitude` (vertical bounce in pixels), `--tilt` (lean angle in
degrees), and `--sway` (horizontal shift in pixels) control how strong the
effect is; `--step-frames` and `-a`/audio work the same as in
`pose_video.py`, since both share the same rendering code
(`render_pose_video`).

### Making the head nod independently of the body (no seams, no extra AI calls)

Rotating a limb cut out of a detailed illustration turns out to be
fragile (see `body_wiggle.py` above) because a limb's outline changes
shape as it rotates, so any resampling error shows up as a visible seam.
`talking_head_video.py` avoids that by keeping the head a separate layer
from a completely static body, and it composites the current mouth shape
onto the head *first*, then rotates/shifts that whole head+mouth piece as
one unit and pastes it onto the body — so the mouth always rides along
with the head's motion instead of drifting off-face.

The best results come from generating the head and body as **two
separate "no-neck" pieces from the start**, rather than cutting a head
out of one merged illustration after the fact:

- generate a head-only image: face + hair, cropped tight at the jaw,
  nothing below it (no neck, no shoulders)
- generate a body-only image: shoulders/torso wearing a high collar
  (e.g. a turtleneck) that closes off where the neck would be, so there's
  no neck skin drawn anywhere — no head, no chin, no face
- paste the head so its jaw sits just inside the collar opening

Since neither piece ever *had* a neck to misalign, the head can nod at
any angle with no post-hoc patching. `assets/sample_character_v3/` is
built this way (two separate AI-generated images, composited once by
code). Earlier `assets/sample_character_v2/` shows the fallback for when
you only have one already-merged illustration to work with: a mediapipe
face-landmarker traces the actual jaw contour (smoothed into a circular
top for zero-seam rotation), and the leftover neck skin below it is
recolored to match the collar. Both work with the same script and folder
format — v3 just needs less correction because nothing was fused in the
first place.

Try it immediately with a built-in placeholder head/body character:

```bash
python talking_head_video.py -o talking_head.mp4 -a path/to/speech.mp3
```

To use your own character, pass a folder built with a head/body split:

```bash
python talking_head_video.py -c path/to/character_dir -a path/to/speech.mp3 -o talking_head.mp4
```

The character folder needs:

- `body.png` - the character with no head/neck, on a canvas with a flat
  background above the collar for the head to sit in
- `head.png` - a cutout of just the head (feathered edge), with
  everywhere outside it transparent
- `mouth_closed.png`, `mouth_mid.png`, `mouth_open.png` - mouth overlays
  cropped to the same canvas and position as `head.png`
- `head_meta.txt` - one line, `... box=(left, top, right, bottom)`,
  giving the head's position on `body.png`

`--nod-step-frames` and `--nod-amplitude` control how often and how far
the head tilts; `-s`/`--speed` controls mouth reaction speed, same as
`lipsync_video.py`.

## Running

Just run the script directly with Python 3.

## Tests

```bash
python -m unittest test_greet.py
python -m unittest test_animate_image.py
python -m unittest test_lipsync_video.py
python -m unittest test_pose_video.py
python -m unittest test_body_wiggle.py
python -m unittest test_talking_head_video.py
```
