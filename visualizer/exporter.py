import numpy as np
from moviepy import VideoClip, AudioFileClip
from tqdm import tqdm

def export_video(output_path, audio_path, render_func, n_frames, fps):
    """
    Assembles the rendered frames and original audio into a final MP4 video.

    render_func: A function that takes a frame index `t` (in seconds) and returns a numpy array representing the frame.
    """

    # We will use a progress bar
    pbar = tqdm(total=n_frames, desc="Rendering Frames")

    def make_frame(t):
        # Calculate frame index based on time and FPS
        frame_idx = int(t * fps)

        # Ensure we don't go out of bounds (can happen due to floating point precision)
        if frame_idx >= n_frames:
            frame_idx = n_frames - 1

        # Call the rendering function
        frame_image = render_func(frame_idx)

        # Convert PIL Image to numpy array (H, W, C) for MoviePy
        frame_array = np.array(frame_image)

        # Update progress bar
        # Note: MoviePy might not call make_frame exactly sequentially or might call it multiple times,
        # but for typical VideoClip generation, it is usually sequential.
        # We handle pbar updating here carefully.
        pbar.update(1)

        return frame_array

    duration = n_frames / fps

    # Create the video clip
    video = VideoClip(make_frame, duration=duration)

    # Attach audio
    audio = AudioFileClip(audio_path)

    # Trim audio to match video duration if needed, or vice-versa
    # Ensure we don't try to subclip beyond the actual audio duration
    actual_duration = min(duration, audio.duration) if audio.duration else duration
    audio = audio.subclipped(0, actual_duration)
    video = video.with_audio(audio)

    # Export the final video
    # We use libx264 for compatibility and aac for audio
    video.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        logger=None # We are using our own tqdm progress bar for frames
    )

    pbar.close()
    audio.close()
    video.close()
