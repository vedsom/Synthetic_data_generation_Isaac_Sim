# Draw Actor SDG object_detection boxes on one rgb frame (filters hidden/tiny objects).
import json
from collections import Counter
from PIL import Image, ImageDraw

RUN = "/media/omv-200/New Volume2/Abhishek/synthetic_data_gen/IRA_Output_3"
CAM, FRAME, MAX_OCC, MIN_PX = "_World_cameras_Camera_1", "00000", 0.8, 10
COLORS = {"box": "yellow", "pallet": "cyan", "barel": "blue", "crate": "lime", "bottle": "magenta", "forklift": "red"}

img = Image.open(f"{RUN}/{CAM}/rgb/rgb_{FRAME}.png").convert("RGB")
det = json.load(open(f"{RUN}/{CAM}/object_detection/object_detection_{FRAME}.json"))
draw, kept = ImageDraw.Draw(img), Counter()
for obj in det["objects"].values():
    cls = obj.get("label", {}).get("class", "?")
    bb = obj.get("annotators", {}).get("bounding_box_2d_tight_fast")
    if not bb or bb.get("occlusionRatio", 0) > MAX_OCC:
        continue
    if bb["x_max"] - bb["x_min"] < MIN_PX or bb["y_max"] - bb["y_min"] < MIN_PX:
        continue
    kept[cls] += 1; c = COLORS.get(cls, "white")
    draw.rectangle([bb["x_min"], bb["y_min"], bb["x_max"], bb["y_max"]], outline=c, width=2)
    draw.text((bb["x_min"] + 3, bb["y_min"] + 2), cls, fill=c)
img.save(f"check_{CAM}_{FRAME}.png"); print(dict(kept))
