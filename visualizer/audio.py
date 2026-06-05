import librosa
import numpy as np

def analyze_audio(audio_path, fps=30, n_bins=64, duration=None):
    """
    Analyzes an audio file and extracts features for visualization.

    Returns:
        dict: A dictionary containing:
            - 'fps': Frames per second
            - 'n_frames': Total number of frames
            - 'fft_bands': (n_frames, n_bins) array of smoothed frequency bands
            - 'rms': (n_frames,) array of RMS energy
            - 'beats': (n_frames,) boolean array, True if beat occurs in this frame
            - 'onset_env': (n_frames,) array of onset strength
            - 'duration': Total audio duration in seconds
            - 'y': The raw audio time series
            - 'sr': The sample rate
    """
    # Load audio
    y, sr = librosa.load(audio_path, sr=None, duration=duration)

    # Calculate hop length to match the video FPS
    hop_length = int(sr / fps)

    # Extract RMS energy
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

    # Extract Mel Spectrogram (used as our FFT bands)
    # Using a slightly higher n_mels and then combining/selecting might be needed,
    # but librosa's melspectrogram with n_mels=n_bins is perfect.
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=hop_length, n_mels=n_bins)

    # Convert to log scale (dB) for better visual scaling
    S_dB = librosa.power_to_db(S, ref=np.max)

    # Normalize S_dB to [0, 1] range
    # S_dB is typically in range [-80, 0]
    S_norm = (S_dB - S_dB.min()) / (S_dB.max() - S_dB.min() + 1e-6)

    # Transpose to shape (n_frames, n_bins)
    fft_bands = S_norm.T

    # Extract onset envelope
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

    # Normalize onset envelope
    onset_env_norm = onset_env / (onset_env.max() + 1e-6)

    # Detect beats
    _, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length)

    # Ensure all feature arrays have the same number of frames
    n_frames = min(len(rms), len(fft_bands), len(onset_env_norm))

    rms = rms[:n_frames]
    fft_bands = fft_bands[:n_frames]
    onset_env_norm = onset_env_norm[:n_frames]

    # Normalize RMS
    rms = rms / (rms.max() + 1e-6)

    # Create boolean beat array
    beats = np.zeros(n_frames, dtype=bool)
    valid_beats = beat_frames[beat_frames < n_frames]
    beats[valid_beats] = True

    actual_duration = len(y) / sr

    return {
        'fps': fps,
        'n_frames': n_frames,
        'fft_bands': fft_bands,
        'rms': rms,
        'beats': beats,
        'onset_env': onset_env_norm,
        'duration': actual_duration,
        'y': y,
        'sr': sr
    }
