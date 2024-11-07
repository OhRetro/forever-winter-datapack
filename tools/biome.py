import os
import json
import re

with open("./settings.json", "r", encoding="utf-8") as file:
    SETTINGS: dict = json.load(file)

# Merge dicts without overwriting
def merge_dicts(dict_a: dict, dict_b: dict):
    for key, value in dict_b.items():
        if isinstance(value, dict) and key in dict_a and isinstance(dict_a[key], dict):
            merge_dicts(dict_a[key], value)
        else:
            dict_a[key] = value
            # print(f"updated dict A \"{key}\" = {value}")
            
def filter(directory: str):
    # filter_words = (
    #     "snowy", "frozen", "ice",
    #     "cold", "winter"
    # )
    
    filter_words = (
        "snowy", 
    )
    
    filter_pattern = re.compile(rf"(_({'|'.join(filter_words)})_)|^({'|'.join(filter_words)})_|_({'|'.join(filter_words)})$")
    
    filter_count = {
        "not_overworld": [],
        "already_cold": []
    }
    
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            filenamenoext = filename.removesuffix(".json")
            
            # Tries to filter out the nether and end biomes
            if "minecraft:freeze_top_layer" not in json.dumps(data):
                os.remove(file_path)
                filter_count["not_overworld"].append(filenamenoext)
                
            # Filters out already cold biomes
            elif filter_pattern.search(filenamenoext):
                os.remove(file_path)
                filter_count["already_cold"].append(filenamenoext)

    return filter_count

def apply_values(directory: str, mode: str):
    template: dict = SETTINGS["template"]
    
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            
            with open(file_path, "r") as file:
                data: dict = json.load(file)

            merge_dicts(data, template.get(mode, "1.19.4"))

            effects: dict = data.get("effects", {})
            effects.pop("grass_color", None)
            effects.pop("foliage_color", None)

            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)

if __name__ == "__main__":
    width = 100
    
    datapacks: list[dict] = SETTINGS.get("datapacks")
    for datapack in datapacks:
        datapack_name: str = datapack["name"]
        print(f"[Datapack: {datapack_name}]".center(width, "="))
        datapack_dir = f"../datapacks/{datapack_name}"
        
        datapack_namespaces: list[str] = datapack["namespaces"]
        for datapack_namespace in datapack_namespaces:
            target_dir = f"{datapack_dir}/data/{datapack_namespace}/worldgen/biome"
            print(f"[{datapack_name}] namespace: {datapack_namespace}")
            filter_count = filter(target_dir)
            print(f"[{datapack_name}] filtered: {len(filter_count["not_overworld"])} not overworld biomes, {len(filter_count["already_cold"])} already cold biomes")
            apply_values(target_dir, datapack["mode"])
            print(f"[{datapack_name}] applied\n")
            
        datapack_overlays: list[dict] = datapack.get("overlays")
        
        for datapack_overlay in datapack_overlays:
            datapack_overlay_dir: str = datapack_overlay["dir"]
            print(f"Overlay: {datapack_overlay_dir}")
            
            datapack_overlay_namespaces: list[str] = datapack_overlay["namespaces"]

            for datapack_overlay_namespace in datapack_overlay_namespaces:
                target_dir = f"{datapack_dir}/{datapack_overlay_dir}/data/{datapack_overlay_namespace}/worldgen/biome"
                print(f"[{datapack_overlay_dir}] namespace: {datapack_overlay_namespace}")
                filter_count = filter(target_dir)
                print(f"[{datapack_overlay_dir}] filtered: {len(filter_count["not_overworld"])} not overworld biomes, {len(filter_count["already_cold"])} already cold biomes")
                apply_values(target_dir, datapack_overlay["mode"])
                print(f"[{datapack_overlay_dir}] applied\n")
        
        print("".center(width, "="))
        