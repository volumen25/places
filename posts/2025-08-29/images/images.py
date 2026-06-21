#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import sys

# === Settings ===
folder = Path(__file__).parent        # Script folder (one level above images/)
base_name = "Whistler"                # Base name for images and markdown
ext = ".jpeg"                         # Desired final extension (keep the dot)
images_subfolder = folder / "images"  # Expected images folder
output_md = folder / f"{base_name}.md"  # Markdown output file

# Normalize extension
if not ext.startswith("."):
    ext = "." + ext

def find_images_folder(fld):
    """Try default 'images' first; if missing, search for a likely images dir (case-insensitive)."""
    if (fld / "images").exists():
        return fld / "images"
    # naive search for any subfolder whose name looks like images/photos/pics
    candidates = [d for d in fld.iterdir() if d.is_dir() and any(k in d.name.lower() for k in ("image", "images", "photo", "photos", "pic", "pics"))]
    if candidates:
        print("Note: using detected folder:", candidates[0].name)
        return candidates[0]
    return None

def get_image_date(file_path):
    """Get photo date from EXIF DateTimeOriginal, fallback to modified time."""
    try:
        with Image.open(file_path) as img:
            exif = img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "DateTimeOriginal" and isinstance(value, str):
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.fromtimestamp(file_path.stat().st_mtime)

# Resolve images folder
if not images_subfolder.exists():
    detected = find_images_folder(folder)
    if detected is None:
        print(f"ERROR: no images folder found at '{images_subfolder}' and no candidate directories detected.")
        print("Directory listing of script folder:")
        for p in sorted(folder.iterdir()):
            print("  ", p.name)
        sys.exit(1)
    images_subfolder = detected

print(f"Looking for images in: {images_subfolder.resolve()}")

# Collect files (case-insensitive jpg/jpeg/png allowed — adjust if you prefer only jpeg)
allowed_exts = {".jpg", ".jpeg", ".png"}
image_files = sorted(
    [f for f in images_subfolder.iterdir() if f.is_file() and f.suffix.lower() in allowed_exts],
    key=get_image_date
)

print(f"Found {len(image_files)} image(s).")
if len(image_files) == 0:
    print("Files present in the images folder:")
    for f in sorted(images_subfolder.iterdir()):
        print("  ", f.name)
    sys.exit(1)

# Prepare numbering width (e.g., 001 if >99)
width = max(2, len(str(len(image_files))))

# Two-pass safe rename inside images_subfolder to avoid collisions
temp_prefix = "__tmprename__"
temp_paths = []
print("Renaming to temporary names...")
for idx, file in enumerate(image_files, start=1):
    temp_name = f"{temp_prefix}{idx:0{width}d}{file.suffix.lower()}"
    temp_path = images_subfolder / temp_name
    file.rename(temp_path)
    temp_paths.append(temp_path)
    print(f"  {file.name} -> {temp_name}")

# Final rename to base_nameNN.ext
print("Renaming temporary files to final names...")
final_names = []
for idx, temp in enumerate(temp_paths, start=1):
    final_name = f"{base_name}{idx:0{width}d}{ext}"
    final_path = images_subfolder / final_name
    temp.rename(final_path)
    final_names.append(final_name)
    print(f"  {temp.name} -> {final_name}")

# Generate Markdown next to script, referencing images/<file>
print(f"\nGenerating Markdown file: {output_md}")
with open(output_md, "w", encoding="utf-8") as md:
    display_name = base_name.capitalize()
    for name in final_names:
        md.write(f'![{display_name}](images/{name}){{group="{display_name}"}}\n\n')

print("\nDone! Summary:")
print(f"  Total images processed: {len(final_names)}")
print(f"  Markdown written to: {output_md.resolve()}")
print(f"  Renamed images are in: {images_subfolder.resolve()}")