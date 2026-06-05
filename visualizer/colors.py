import colorsys
from colorthief import ColorThief

def extract_colors(image_path, num_colors=5):
    """
    Extracts dominant colors from an image and derives a primary accent color
    and a secondary glow color ensuring high contrast/saturation.

    Returns:
        tuple: (primary_color, secondary_color) as RGB tuples.
    """
    color_thief = ColorThief(image_path)
    palette = color_thief.get_palette(color_count=num_colors)

    # We want colors that are relatively saturated and bright for the visualizer
    def color_score(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        # Score heavily based on saturation and value to get vibrant colors
        return s * v

    # Sort palette by our score to get the most vibrant colors
    sorted_palette = sorted(palette, key=color_score, reverse=True)

    # Primary accent color will be the most vibrant
    primary_color = sorted_palette[0]

    # Secondary color (glow) will be the second most vibrant, or a slightly adjusted primary if palette is dull
    if len(sorted_palette) > 1:
        secondary_color = sorted_palette[1]
    else:
        # Fallback if somehow only one color is returned
        primary_color = palette[0]
        secondary_color = (min(255, primary_color[0] + 50),
                           min(255, primary_color[1] + 50),
                           min(255, primary_color[2] + 50))

    return primary_color, secondary_color

def interpolate_color(color1, color2, factor):
    """
    Interpolate between two RGB colors.
    factor: 0.0 returns color1, 1.0 returns color2.
    """
    return (
        int(color1[0] + (color2[0] - color1[0]) * factor),
        int(color1[1] + (color2[1] - color1[1]) * factor),
        int(color1[2] + (color2[2] - color1[2]) * factor)
    )
