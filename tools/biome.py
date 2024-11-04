import os
import json

# Snowy Taiga Settings
TARGET_VALUES = {
    "downfall": 0.4,
    "temperature": -0.5,
    "effects": {
        "fog_color": 12638463,
        "sky_color": 8625919,
        "water_color": 4020182,
        "water_fog_color": 329011,
    },
    "has_precipitation": True
}

# Merge dicts without overwriting
def merge_dicts(dict_a: dict, dict_b: dict):
    for key, value in dict_b.items():
        if isinstance(value, dict) and key in dict_a and isinstance(dict_a[key], dict):
            merge_dicts(dict_a[key], value)
        else:
            dict_a[key] = value
            print(f"updated dict A \"{key}\" = {value}")
            
def filter(directory: str):
    print("filtering biomes...")
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            
            with open(file_path, "r") as file:
                data = json.load(file)

            # Tries to filter out the nether and end biomes
            if "minecraft:freeze_top_layer" not in json.dumps(data):
                os.remove(file_path)
                print(f"deleted not overworld biomes: {filename}")
                
            elif filename.startswith(("snowy_", "frozen_", "ice_")):
                os.remove(file_path)
                print(f"deleted already cold biomes: {filename}")


def apply_values(directory: str):
    print("applying values...")
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            print(f"applying values to \"{filename}\"")
            file_path = os.path.join(directory, filename)
            
            with open(file_path, "r") as file:
                data: dict = json.load(file)

            merge_dicts(data, TARGET_VALUES)

            effects: dict = data.get("effects", {})
            effects.pop("grass_color", None)
            effects.pop("foliage_color", None)

            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
                
            print("")

if __name__ == "__main__":
    target_ver = "1_20"
    target_dir = f"../datapacks/fw{target_ver}/data/minecraft/worldgen/biome"
    filter(target_dir)
    apply_values(target_dir)