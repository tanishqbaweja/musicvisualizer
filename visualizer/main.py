import argparse
import sys
import os

# Add the parent directory of 'visualizer' to sys.path so we can import modules
# when running main.py directly without setting PYTHONPATH.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from visualizer.colors import extract_colors
from visualizer.audio import analyze_audio
from visualizer.renderer import prepare_background, render_frame
from visualizer.exporter import export_video

def main():
    parser = argparse.ArgumentParser(description="Python CLI music visualizer")
    parser.add_argument("--audio", required=True, help="Path to an audio file (MP3/WAV)")
    parser.add_argument("--image", required=True, help="Path to a background image (JPG/PNG)")
    parser.add_argument("--output", default="output.mp4", help="Output video path (default: output.mp4)")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
    parser.add_argument("--duration", type=float, default=None, help="Optional clip duration cap in seconds")

    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        sys.exit(1)

    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)

    print(f"Extracting colors from {args.image}...")
    primary_color, secondary_color = extract_colors(args.image)
    print(f"Primary Color: {primary_color}, Secondary Color: {secondary_color}")

    print(f"Analyzing audio {args.audio}...")
    audio_data = analyze_audio(args.audio, fps=args.fps, duration=args.duration)

    n_frames = audio_data['n_frames']
    duration = audio_data['duration']
    print(f"Analysis complete: {n_frames} frames, {duration:.2f} seconds.")

    print(f"Preparing background image...")
    bg_image = prepare_background(args.image, size=(1920, 1080))

    print(f"Starting rendering pipeline...")

    def get_frame_data(idx):
        if idx < 0 or idx >= n_frames:
            return None
        return {
            'fft': audio_data['fft_bands'][idx],
            'rms': audio_data['rms'][idx],
            'is_beat': audio_data['beats'][idx],
            'onset': audio_data['onset_env'][idx]
        }

    # Render function for MoviePy
    # We use a closure to keep track of the last rendered frame for smoothing (though MoviePy might request frames out of order, it usually doesn't for simple writing)
    # A robust approach computes the exact interpolation factor if needed, but for frame-by-frame rendering, t * fps is exact.

    def render_func(frame_idx):
        # We add some interpolation smoothing logic based on frame indices
        current_data = get_frame_data(frame_idx)
        prev_data = get_frame_data(frame_idx - 1) if frame_idx > 0 else current_data

        # We always render exactly on the frame, so interpolation factor from previous frame is fixed
        # For smoother movement, lerping over multiple frames could be used, but since we precomputed
        # features *at* the frame rate, we just lerp between the previous frame's features and current.
        # Actually, since features are already computed per-frame, we use factor=1.0 to just use current.
        # But wait, the requirement says "lerp the bar heights". We can apply an EMA (Exponential Moving Average)
        # to the FFT bins *before* rendering, or just use the current frame's data which is already derived from a smoothed STFT window.
        # Let's apply a simple smoothing here where interpolation_factor=0.5 (average of prev and current)
        # or just 1.0 (use current directly, since mel spectrogram is already windowed).
        # We'll use 0.5 to smooth it visually.
        interpolation_factor = 0.5

        return render_frame(bg_image, primary_color, secondary_color, current_data, prev_data, interpolation_factor)

    print(f"Exporting video to {args.output}...")
    export_video(args.output, args.audio, render_func, n_frames, args.fps)

    print(f"Done! Saved to {args.output}")

if __name__ == "__main__":
    main()
