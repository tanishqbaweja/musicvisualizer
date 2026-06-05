import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

def prepare_background(image_path, size=(1920, 1080)):
    """
    Loads, resizes (cropping to fit), and darkens the background image.
    """
    img = Image.open(image_path).convert('RGBA')

    # Calculate aspect ratios
    img_ratio = img.width / img.height
    target_ratio = size[0] / size[1]

    # Crop to maintain aspect ratio
    if img_ratio > target_ratio:
        # Image is wider, crop sides
        new_width = int(target_ratio * img.height)
        offset = (img.width - new_width) // 2
        img = img.crop((offset, 0, offset + new_width, img.height))
    else:
        # Image is taller, crop top/bottom
        new_height = int(img.width / target_ratio)
        offset = (img.height - new_height) // 2
        img = img.crop((0, offset, img.width, offset + new_height))

    img = img.resize(size, Image.Resampling.LANCZOS)

    # Darken to ~30% brightness
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.3)

    return img

def create_glow(image, radius=20):
    """Applies a gaussian blur to create a glow effect."""
    return image.filter(ImageFilter.GaussianBlur(radius=radius))

def render_frame(bg_image, primary_color, secondary_color, frame_data, prev_frame_data, interpolation_factor):
    """
    Renders a single frame of the visualizer.

    frame_data/prev_frame_data: dict with 'fft', 'rms', 'is_beat', 'onset'
    interpolation_factor: float [0, 1] for smoothing between frames
    """
    # Create a copy of the background to draw on
    width, height = bg_image.size
    center_x, center_y = width // 2, height // 2

    # Setup rendering layers
    frame = Image.new('RGBA', bg_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)

    # Interpolate FFT values
    current_fft = frame_data['fft']
    prev_fft = prev_frame_data['fft'] if prev_frame_data else current_fft
    fft_smoothed = prev_fft + (current_fft - prev_fft) * interpolation_factor

    # Interpolate RMS and onset
    current_rms = frame_data['rms']
    prev_rms = prev_frame_data['rms'] if prev_frame_data else current_rms
    rms_smoothed = prev_rms + (current_rms - prev_rms) * interpolation_factor

    # Beat flash (Vignette pulse)
    if frame_data['is_beat']:
        # Create a radial gradient vignette
        pulse_intensity = int(100 * frame_data['onset']) # Max alpha 100
        pulse_color = (*primary_color, pulse_intensity)
        # Simplified pulse: draw a large rectangle with low opacity
        # A true vignette would use an alpha mask, for speed we use a filled rect
        # Or even better, a radial fade. We'll do a simple transparent overlay.
        vignette_layer = Image.new('RGBA', bg_image.size, pulse_color)
        frame.alpha_composite(vignette_layer)

    # Visualizer dimensions
    n_bars = len(fft_smoothed)
    base_radius = min(width, height) * 0.2 + (rms_smoothed * min(width, height) * 0.05)
    max_bar_height = min(width, height) * 0.25

    # Draw bars
    bar_width = 8

    # Create a separate layer for glow
    glow_layer = Image.new('RGBA', bg_image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    waveform_points = []

    for i in range(n_bars):
        # Calculate angle
        angle = (i / n_bars) * 2 * math.pi - (math.pi / 2) # Start at top

        # Calculate height
        val = fft_smoothed[i]
        # Make the height somewhat exponential for better visual pop
        height_val = (val ** 1.5) * max_bar_height

        # Inner and outer points
        x1 = center_x + math.cos(angle) * base_radius
        y1 = center_y + math.sin(angle) * base_radius

        x2 = center_x + math.cos(angle) * (base_radius + height_val)
        y2 = center_y + math.sin(angle) * (base_radius + height_val)

        # Color interpolation based on height/value
        color_factor = min(1.0, max(0.0, val * 1.5))
        r = int(secondary_color[0] + (primary_color[0] - secondary_color[0]) * color_factor)
        g = int(secondary_color[1] + (primary_color[1] - secondary_color[1]) * color_factor)
        b = int(secondary_color[2] + (primary_color[2] - secondary_color[2]) * color_factor)

        bar_color = (r, g, b, 255)

        # Shadow
        shadow_offset = 4
        shadow_color = (0, 0, 0, 150)
        draw.line([(x1 + shadow_offset, y1 + shadow_offset),
                   (x2 + shadow_offset, y2 + shadow_offset)],
                  fill=shadow_color, width=bar_width)

        # Draw actual bar
        draw.line([(x1, y1), (x2, y2)], fill=bar_color, width=bar_width)

        # Draw glow on peaks
        if val > 0.6:
            glow_draw.line([(x1, y1), (x2, y2)], fill=(r, g, b, int(150 * val)), width=bar_width * 2)

        # Collect points for subtle waveform
        waveform_points.append((x2, y2))

    # Close the waveform loop
    if waveform_points:
        waveform_points.append(waveform_points[0])
        draw.line(waveform_points, fill=(255, 255, 255, 80), width=2, joint="curve")

    # Apply glow filter and composite
    glow_layer = create_glow(glow_layer, radius=10)
    frame.alpha_composite(glow_layer)

    # Composite the frame onto the background
    final_frame = Image.alpha_composite(bg_image, frame)

    return final_frame.convert('RGB')
