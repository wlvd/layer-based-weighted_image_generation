import json
from PIL import Image

file_path = input("image path: ")

img = Image.open(file_path)

print("\n--- metadata ---")
print(img.text)

if "traits" in img.text:
    print("\n--- traits ---")
    data = json.loads(img.text["traits"])
    print(json.dumps(data, indent=1))
else:
    print("\nNo 'traits' metadata found.")