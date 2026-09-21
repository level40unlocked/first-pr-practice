# first-pr-practice

A tiny practice project for learning the GitHub first-PR workflow.

## What's here

- `greet.py` - a small function that returns a greeting for a given name.
- `animate_image.py` - turns a still 2D image into a short video with a
  simple pan/zoom (Ken Burns) animation.

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

## Running

Just run the script directly with Python 3.

## Tests

```bash
python -m unittest test_greet.py
python -m unittest test_animate_image.py
```
