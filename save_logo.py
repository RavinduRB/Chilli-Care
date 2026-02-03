"""
Save the Chilli Care logo to the static/images folder.
Please save your logo image as 'chilli-care-logo.png' in the static/images/ directory.

The logo should be:
- PNG format with transparent background
- Recommended dimensions: 300-500px width
- The image from your attachment showing "Chilli Care" with the chilli pepper and magnifying glass icon
"""

import os

# Ensure the images directory exists
images_dir = os.path.join("static", "images")
os.makedirs(images_dir, exist_ok=True)

logo_path = os.path.join(images_dir, "chilli-care-logo.png")

print(f"Please save your Chilli Care logo image to:")
print(f"  {os.path.abspath(logo_path)}")
print()
print("The logo has been integrated into all HTML templates.")
print("Once you save the image file, refresh your browser to see it.")
