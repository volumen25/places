#!/usr/bin/env python3
from pathlib import Path

# === Settings ===
folder = Path(__file__).parent        # Script folder (one level above images/)
base_name = "Japan"                # Base name for images and text output
ext = ".jpeg"                         # Desired final extension (keep the dot)
images_subfolder = folder / "images"  # Expected images folder
output_txt = images_subfolder / f"{base_name}.txt"  # TXT output file

def normalize_and_rename_images():
    """
    Find image files in images_subfolder, normalize names to:
    base_name + zero-padded number + ext
    Example: Japan01.jpeg, Japan02.jpeg ...
    """
    if not images_subfolder.exists():
        print(f"Error: {images_subfolder} does not exist.")
        return []

    # Collect only image files with given extension or common formats
    valid_exts = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    files = [f for f in images_subfolder.iterdir() if f.suffix.lower() in valid_exts]

    if not files:
        print("No images found.")
        return []

    # Sort by name
    files.sort()

    renamed_files = []
    for i, f in enumerate(files, start=1):
        new_name = f"{base_name}{i:02d}{ext}"
        new_path = f.with_name(new_name)
        if f != new_path:
            f.rename(new_path)
        renamed_files.append(new_path)

    print(f"Processed {len(renamed_files)} image(s).")
    return renamed_files

def generate_text(images):
    """
    Write TXT file with one image per line, captions from filenames.
    """
    lines = []
    for img in images:
        label = img.stem  # e.g., Japan01
        line = f'![{label}](images/{img.name}){{group="{base_name}"}}'
        lines.append(line)

    output_txt.write_text("\n\n".join(lines), encoding="utf-8")
    print(f"Text gallery written to {output_txt}")

def main():
    images = normalize_and_rename_images()
    if images:
        generate_text(images)

if __name__ == "__main__":
    main()