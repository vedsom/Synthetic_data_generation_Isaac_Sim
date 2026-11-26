# Convert Actor SDG output (object_detection JSON + rgb) to a YOLO dataset.
import os, json, glob, shutil
from collections import Counter
from PIL import Image

RUN = "/media/omv-200/New Volume2/Abhishek/synthetic_data_gen/IRA_Output_3"
DST = RUN + "_yolo"
CLASSES = ["box", "pallet", "barel", "crate", "bottle", "forklift"]
VAL_CAMS = {"_World_cameras_Camera_5"}      # check every class still appears in train!
MAX_OCC, MIN_PX = 0.8, 10

for split in ("train", "val"):
    os.makedirs(f"{DST}/images/{split}", exist_ok=True); os.makedirs(f"{DST}/labels/{split}", exist_ok=True)
counts, n_img = Counter(), Counter()
for det_path in sorted(glob.glob(f"{RUN}/*/object_detection/object_detection_*.json")):
    cam = det_path.split(os.sep)[-3]; fid = os.path.basename(det_path).split("_")[-1].split(".")[0]
    rgb = f"{RUN}/{cam}/rgb/rgb_{fid}.png"
    if not os.path.exists(rgb):
        continue
    W, H = Image.open(rgb).size; lines = []
    for obj in json.load(open(det_path))["objects"].values():
        cls = obj.get("label", {}).get("class"); bb = obj.get("annotators", {}).get("bounding_box_2d_tight_fast")
        if cls not in CLASSES or not bb:
            continue
        x0, y0, x1, y1 = max(0, bb["x_min"]), max(0, bb["y_min"]), min(W, bb["x_max"]), min(H, bb["y_max"])
        if bb.get("occlusionRatio", 0) > MAX_OCC or (x1 - x0) < MIN_PX or (y1 - y0) < MIN_PX:
            continue
        lines.append(f"{CLASSES.index(cls)} {(x0+x1)/2/W:.6f} {(y0+y1)/2/H:.6f} {(x1-x0)/W:.6f} {(y1-y0)/H:.6f}")
        counts[cls] += 1
    split = "val" if cam in VAL_CAMS else "train"; stem = f"{cam.strip('_')}_{fid}"
    shutil.copy(rgb, f"{DST}/images/{split}/{stem}.png")
    open(f"{DST}/labels/{split}/{stem}.txt", "w").write("\n".join(lines)); n_img[split] += 1
with open(f"{DST}/data.yaml", "w") as f:
    f.write(f"path: {DST}\ntrain: images/train\nval: images/val\nnames:\n")
    f.writelines(f"  {i}: {c}\n" for i, c in enumerate(CLASSES))
print(dict(n_img), dict(counts))
