import numpy as np
from scipy.io import wavfile
from PIL import Image

def generate_dummy_assets():
    # 1. Generate Dummy Audio
    sample_rate = 44100
    duration = 5.0 # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Create a compound wave: 440 Hz (A4) and a pulsing 60 Hz bass
    wave1 = 0.5 * np.sin(2 * np.pi * 440 * t)
    # Pulse the bass to trigger beat detection
    pulse = (np.sin(2 * np.pi * 2 * t) + 1) / 2 # 2 Hz pulse
    wave2 = 0.5 * np.sin(2 * np.pi * 60 * t) * pulse

    audio_data = wave1 + wave2

    # Normalize to 16-bit PCM range
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

    wavfile.write("dummy.wav", sample_rate, audio_data)
    print("Generated dummy.wav")

    # 2. Generate Dummy Image
    width, height = 1920, 1080
    # Create a gradient image
    img_array = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        # A deep purple to orange gradient
        r = int(255 * (y / height))
        g = int(100 * (y / height))
        b = int(255 * (1 - y / height))
        img_array[y, :, :] = [r, g, b]

    img = Image.fromarray(img_array)
    img.save("dummy.png")
    print("Generated dummy.png")

if __name__ == "__main__":
    generate_dummy_assets()
