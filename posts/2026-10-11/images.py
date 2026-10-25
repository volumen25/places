#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = ["pillow"]
# ///
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import IFD, Base

# === Settings ===
FOLDER = Path(__file__).resolve().parent  # Folder containing the script and images/
BASE_NAME = "Hokkaido"                    # Base name for images and output file
EXT = ".jpeg"                             # Final extension
ALLOWED_EXTS = {".jpg", ".jpeg", ".png"}  # Input extensions (case-insensitive)
TEMP_PREFIX = "__tmprename__"
IMAGE_FOLDER_HINTS = ("image", "photo", "pic")

ext = EXT if EXT.startswith(".") else f".{EXT}"
output = FOLDER / f"{BASE_NAME}.txt"


def find_images_folder(parent: Path) -> Path | None:
    """Return parent/images, or the first subfolder whose name looks like an image folder."""
    default = parent / "images"
    if default.is_dir():
        return default
    candidates = sorted(
        d for d in parent.iterdir()
        if d.is_dir() and any(hint in d.name.lower() for hint in IMAGE_FOLDER_HINTS)
    )
    if candidates:
        print(f"Note: using detected folder: {candidates[0].name}")
        return candidates[0]
    return None


def get_image_date(path: Path) -> datetime:
    """Return EXIF DateTimeOriginal, falling back to the file's modified time."""
    try:
        with Image.open(path) as img:
            value = img.getexif().get_ifd(IFD.Exif).get(Base.DateTimeOriginal)
        if isinstance(value, str):
            return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except (OSError, ValueError):
        pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def list_dir(path: Path) -> None:
    for p in sorted(path.iterdir()):
        print(f"  {p.name}")


# Resolve images folder
images_dir = find_images_folder(FOLDER)
if images_dir is None:
    print(f"ERROR: no images folder found in '{FOLDER}'.")
    print("Directory listing of script folder:")
    list_dir(FOLDER)
    sys.exit(1)

print(f"Looking for images in: {images_dir}")

image_files = sorted(
    (f for f in images_dir.iterdir() if f.is_file() and f.suffix.lower() in ALLOWED_EXTS),
    key=get_image_date,
)

print(f"Found {len(image_files)} image(s).")
if not image_files:
    print("Files present in the images folder:")
    list_dir(images_dir)
    sys.exit(1)

# Numbering width (at least 2 digits, e.g. 001 if there are more than 99 images)
width = max(2, len(str(len(image_files))))

# Two-pass rename to avoid name collisions
print("Renaming to temporary names...")
temp_paths = []
for idx, file in enumerate(image_files, start=1):
    temp_path = images_dir / f"{TEMP_PREFIX}{idx:0{width}d}{file.suffix.lower()}"
    file.rename(temp_path)
    temp_paths.append(temp_path)
    print(f"  {file.name} -> {temp_path.name}")

print("Renaming temporary files to final names...")
final_names = []
for idx, temp in enumerate(temp_paths, start=1):
    final_name = f"{BASE_NAME}{idx:0{width}d}{ext}"
    temp.rename(images_dir / final_name)
    final_names.append(final_name)
    print(f"  {temp.name} -> {final_name}")

# Write the Markdown-style image list next to the script
print(f"\nGenerating text file: {output}")
display_name = BASE_NAME.capitalize()
with output.open("w", encoding="utf-8") as out:
    for name in final_names:
        out.write(f'![{display_name}](images/{name}){{group="{display_name}"}}\n\n')

print("\nDone! Summary:")
print(f"  Total images processed: {len(final_names)}")
print(f"  Text written to: {output}")
print(f"  Renamed images are in: {images_dir}")