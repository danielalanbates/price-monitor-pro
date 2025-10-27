#!/usr/bin/env python3
"""
Create Price Monitor Pro Application Icon
Generates PNG and ICNS format icons for the Electron app
"""

from PIL import Image, ImageDraw, ImageFont
import os
import subprocess

def create_price_monitor_icon(size=1024):
    """Create a price monitor icon with a dollar sign and shopping cart design"""
    # Create a new image with transparent background
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Define colors
    bg_color = (34, 193, 195)  # Teal gradient start
    bg_color_end = (253, 187, 45)  # Yellow gradient end
    icon_color = (255, 255, 255)  # White
    accent_color = (40, 167, 69)  # Green for savings

    # Draw circular gradient background
    center = size // 2
    radius = int(size * 0.45)

    # Draw circle background
    draw.ellipse(
        [(center - radius, center - radius), (center + radius, center + radius)],
        fill=bg_color,
        outline=None
    )

    # Draw dollar sign
    font_size = int(size * 0.5)
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Draw dollar sign ($)
    dollar_text = "$"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), dollar_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text - position it slightly higher to make room for arrow below
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - int(size * 0.12)

    # Draw text with shadow for depth
    shadow_offset = int(size * 0.01)
    draw.text((text_x + shadow_offset, text_y + shadow_offset), dollar_text,
              font=font, fill=(0, 0, 0, 128))
    draw.text((text_x, text_y), dollar_text, font=font, fill=icon_color)

    # Draw downward arrow BELOW the dollar sign (not overlapping)
    arrow_center_x = center
    # Position arrow below the dollar sign
    arrow_start_y = text_y + text_height

    # Draw arrow shaft (vertical line)
    shaft_width = int(size * 0.05)
    shaft_height = int(size * 0.12)
    draw.rectangle([
        (arrow_center_x - shaft_width // 2, arrow_start_y),
        (arrow_center_x + shaft_width // 2, arrow_start_y + shaft_height)
    ], fill=accent_color)

    # Draw arrow head (triangle pointing down)
    arrow_head_size = int(size * 0.1)
    arrow_tip_y = arrow_start_y + shaft_height + arrow_head_size
    arrow_points = [
        (arrow_center_x - arrow_head_size, arrow_start_y + shaft_height),  # Left
        (arrow_center_x + arrow_head_size, arrow_start_y + shaft_height),  # Right
        (arrow_center_x, arrow_tip_y)  # Bottom point
    ]
    draw.polygon(arrow_points, fill=accent_color)

    return image

def save_png_icon(image, output_dir, name="icon"):
    """Save PNG versions of the icon at multiple sizes"""
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    for size in sizes:
        resized = image.resize((size, size), Image.Resampling.LANCZOS)
        output_path = os.path.join(output_dir, f"{name}_{size}.png")
        resized.save(output_path, "PNG")
        print(f"✅ Created: {output_path}")

    # Save main icon.png (512x512 is good for most uses)
    main_icon = image.resize((512, 512), Image.Resampling.LANCZOS)
    main_path = os.path.join(output_dir, f"{name}.png")
    main_icon.save(main_path, "PNG")
    print(f"✅ Created main icon: {main_path}")

    return main_path

def create_iconset(output_dir, name="icon"):
    """Create macOS .iconset directory with all required sizes"""
    iconset_dir = os.path.join(output_dir, f"{name}.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    # macOS icon sizes and naming convention
    icon_sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png")
    ]

    # Load the base image
    base_image = create_price_monitor_icon(1024)

    for size, filename in icon_sizes:
        resized = base_image.resize((size, size), Image.Resampling.LANCZOS)
        output_path = os.path.join(iconset_dir, filename)
        resized.save(output_path, "PNG")
        print(f"✅ Created: {output_path}")

    return iconset_dir

def convert_to_icns(iconset_dir, output_dir, name="icon"):
    """Convert .iconset to .icns using macOS iconutil"""
    icns_path = os.path.join(output_dir, f"{name}.icns")

    try:
        subprocess.run([
            'iconutil',
            '-c', 'icns',
            iconset_dir,
            '-o', icns_path
        ], check=True)
        print(f"✅ Created macOS icon: {icns_path}")
        return icns_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create .icns file: {e}")
        print("Note: iconutil requires macOS")
        return None
    except FileNotFoundError:
        print("❌ iconutil not found (requires macOS)")
        return None

def main():
    """Main entry point"""
    # Determine output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "electron-app", "assets")

    # Create assets directory if it doesn't exist
    os.makedirs(assets_dir, exist_ok=True)

    print("🎨 Creating Price Monitor Pro icon...")
    print(f"📁 Output directory: {assets_dir}\n")

    # Create the icon
    icon_image = create_price_monitor_icon(1024)

    # Save PNG versions
    print("Creating PNG icons...")
    save_png_icon(icon_image, assets_dir, "icon")

    # Create macOS iconset
    print("\nCreating macOS iconset...")
    iconset_dir = create_iconset(assets_dir, "icon")

    # Convert to .icns (macOS only)
    print("\nConverting to .icns format...")
    icns_path = convert_to_icns(iconset_dir, assets_dir, "icon")

    if icns_path:
        print(f"\n✨ Icon creation complete!")
        print(f"📦 Icon files available in: {assets_dir}")
        print(f"   - icon.png (main icon)")
        print(f"   - icon.icns (macOS application icon)")
    else:
        print(f"\n⚠️  Icon creation partially complete")
        print(f"📦 PNG icons available in: {assets_dir}")
        print(f"   - icon.png (main icon)")
        print(f"❌ .icns file could not be created (requires macOS with iconutil)")

if __name__ == "__main__":
    main()
