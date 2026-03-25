import json
import random
from pathlib import Path
from PIL import Image, PngImagePlugin

base_folder = Path(__file__).parent
resource = base_folder / "resources"
output = base_folder / "output"
output.mkdir(exist_ok=True)

ordine_z = [
    "background",
    "body",
    "clothing",
    "neck_acc",
    "mouth",
    "hat",
    "l_eye",
    "r_eye",
]

layer_chances = {
    "background": 1.0,
    "body": 1.0,
    "clothing": 0.1,
    "neck_acc": 0.1,
    "mouth": 1.0,
    "hat": 0.1,
    "l_eye": 1.0,
    "r_eye": 1.0,
}

weights = {
    "background": {
        "default_blue.png": 50,
        "default_green.png": 50,
        "default_red.png": 50,
        "desert.png": 10,
        "moon.png": 5,
    },
    "body": {
        "default_blue.png": 50,
        "default_green.png": 50,
        "golden.png": 1,
        "slime.png": 10,
    },
    "clothing": {
        "suit.png": 5,
        "tank_top.png": 50,
        "tee.png": 30,
    },
    "hat": {
        "atoms.png": 5,
        "cap.png": 50,
        "crown.png": 5,
    },
    "l_eye": {
        "l_blue.png": 50,
        "l_brown.png": 50,
        "l_external.png": 5,
        "l_green.png": 50,
    },
    "r_eye": {
        "r_blue.png": 50,
        "r_brown.png": 50,
        "r_external.png": 5,
        "r_green.png": 50,
    },
    "mouth": {
        "cigar.png": 5,
        "default.png": 100,
        "gum.png": 5,
        "happy.png": 40,
        "vampire.png": 20,
    },
    "neck_acc": {
        "chain.png": 5,
        "scarf.png": 10,
    },
}

seen = []


def pick_trait(layer):
    folder = resource / layer
    files = list(folder.glob("*.png"))

    if len(files) == 0:
        raise Exception(f"No files in {folder}")

    chance = layer_chances.get(layer, 1.0)
    if random.random() > chance:
        return None

    file_weights = []
    for file in files:
        if layer in weights and file.name in weights[layer]:
            file_weights.append(weights[layer][file.name])
        else:
            file_weights.append(1)

    return random.choices(files, weights=file_weights, k=1)[0]


def count_total_combinations():
    total = 1

    for layer in ordine_z:
        folder = resource / layer
        files = list(folder.glob("*.png"))

        if len(files) == 0:
            raise Exception(f"No files in {folder}")

        count = len(files)

        if layer_chances.get(layer, 1.0) < 1.0:
            count += 1

        total = total * count

    return total


def generate(index):
    while True:
        selection = {}

        for layer in ordine_z:
            selection[layer] = pick_trait(layer)

        combo = []
        for layer in ordine_z:
            if selection[layer] is None:
                combo.append("NONE")
            else:
                combo.append(selection[layer].name)

        combo = tuple(combo)

        if combo not in seen:
            seen.append(combo)
            break

    first_image = None
    for layer in ordine_z:
        if selection[layer] is not None:
            first_image = selection[layer]
            break

    if first_image is None:
        raise Exception("No image selected")

    base = Image.open(first_image).convert("RGBA")
    final_image = Image.new("RGBA", base.size, (0, 0, 0, 0))

    for layer in ordine_z:
        if selection[layer] is not None:
            img = Image.open(selection[layer]).convert("RGBA")
            final_image.alpha_composite(img)

    metadata = {
        "name": f"avatar_{index}",
        "attributes": {}
    }

    for layer in ordine_z:
        if selection[layer] is None:
            metadata["attributes"][layer] = None
        else:
            metadata["attributes"][layer] = selection[layer].stem

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("traits", json.dumps(metadata))

    save_path = output / f"avatar_{index}.png"
    final_image.save(save_path, pnginfo=pnginfo)

    print("saved:", save_path)


max_combinations = count_total_combinations()
num_images = int(input(f"number of images (max: {max_combinations}): "))

if num_images < 1:
    print("Need at least 1 image to be generated")

elif num_images > max_combinations:
    print("Too many images requested")

else:
    for i in range(1, num_images + 1):
        generate(i)