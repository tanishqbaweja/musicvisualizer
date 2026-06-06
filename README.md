# Python CLI Music Visualizer

A powerful, high-performance command-line tool that generates stunning, polished music visualization videos from audio and image files. Built with Python, this visualizer uses advanced audio analysis and high-speed frame rendering to create reactive, beautiful visual content.

## Features

- **Intelligent Color Palette:** Automatically extracts dominant colors from your background image using `colorthief` to derive vibrant primary accent and secondary glow colors.
- **Advanced Audio Analysis:** Uses `librosa` to accurately pre-compute RMS energy, FFT frequency bands (~64 bins), onset strength, and beat frame positions.
- **Polished Rendering:** Frame-by-frame rendering using `Pillow` featuring:
  - Background darkening for high contrast.
  - A dynamic radial/circular bar visualizer driven by FFT bins.
  - Smooth color interpolation and drop shadows on visualizer bars.
  - Soft glow/bloom effects on peak frequencies.
  - A subtle waveform line overlaid at low opacity.
  - Vignette pulse effects that trigger precisely on the beat.
- **Fast and Efficient:** All audio features are pre-computed before rendering.
- **Video Assembly:** Uses `moviepy` to seamlessly combine the generated visual frames with the original high-quality audio into an MP4 file.

## Prerequisites

- Python 3.8+
- [FFmpeg](https://ffmpeg.org/) (usually installed automatically by `imageio-ffmpeg` via `moviepy`)

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

```bash
pip install -r visualizer/requirements.txt
```

## Usage

Run the visualizer via the CLI using `visualizer/main.py`. Ensure your `PYTHONPATH` includes the project root directory.

### Basic Command
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python visualizer/main.py --audio your_song.mp3 --image background.jpg
```

### CLI Arguments

| Argument     | Description                                                                 | Default      |
|--------------|-----------------------------------------------------------------------------|--------------|
| `--audio`    | **(Required)** Path to the audio file (MP3/WAV/etc.)                        | -            |
| `--image`    | **(Required)** Path to the background image (JPG/PNG)                       | -            |
| `--output`   | Path to save the final generated video file.                                | `output.mp4` |
| `--fps`      | Frames per second for the output video.                                     | `30`         |
| `--duration` | Optional clip duration cap in seconds (e.g., render only the first 30 secs) | `None`       |

### Example

Generate a 15-second visualizer at 60 FPS:

```bash
python visualizer/main.py --audio track.wav --image cover.png --output visuals.mp4 --fps 60 --duration 15
```

## Project Structure

- `visualizer/main.py` - CLI entry point and execution pipeline.
- `visualizer/audio.py` - Audio loading and `librosa` feature extraction.
- `visualizer/colors.py` - Background image dominant color extraction.
- `visualizer/renderer.py` - Per-frame PIL drawing logic.
- `visualizer/exporter.py` - `moviepy` video assembly and output.

## License

MIT License
