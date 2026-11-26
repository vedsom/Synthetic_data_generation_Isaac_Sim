"""
Build a self-contained web page to explore an Isaac Sim synthetic dataset.

Type an object name ("box", "pallet", "barrel", "all") and every matching object in the
frame is highlighted with its ground-truth bounding box from Replicator.

Run (any Python with Pillow, e.g. your yolo_env, or Isaac Sim's Script Editor):
    python build_explorer.py
Then open the printed .html file in a browser.
"""
import base64
import glob
import io
import json
import os
from collections import Counter

from PIL import Image

# ----------------------------------------------------------------------------- settings
RUN = "/media/omv-200/New Volume2/Abhishek/synthetic_data_gen/IRA_Output_3"   # Actor SDG output
# GitHub Pages serves docs/index.html -> write the page straight there
OUT_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "index.html")

TITLE = "Synthetic Warehouse Dataset"
SUBTITLE = "Generated with NVIDIA Isaac Sim 6.0 Replicator - every label below was created automatically"
AUTHOR = "Abhishek"                    # shown in the page header

FRAMES_PER_CAMERA = 1                  # your frames are near-identical; use None for all frames
WIDTH = 1280                           # export width (keeps the page light)
JPEG_QUALITY = 85
MAX_OCCLUSION_EXPORT = 0.95            # page slider filters further; this just drops ~invisible ones
MIN_PX = 6                             # drop boxes smaller than this (original pixels)

CLASS_COLORS = {                       # class -> colour on the page
    "box": "#ffd23f", "pallet": "#3fd0ff", "barel": "#5b7cff",
    "crate": "#5cff8a", "bottle": "#ff5cd6", "forklift": "#ff5a4f",
}


# ----------------------------------------------------------------------------- helpers
def find_one(pattern):
    hits = sorted(glob.glob(pattern))
    return hits[0] if hits else None


def to_data_uri(img, fmt):
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.convert("RGB").save(buf, "JPEG", quality=JPEG_QUALITY, optimize=True)
        mime = "image/jpeg"
    else:
        img.save(buf, "PNG", optimize=True)
        mime = "image/png"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()


def load_seg(path, size):
    """Segmentation PNGs have a transparent background -> put them on black, keep hard edges."""
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (8, 10, 14, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB").resize(size, Image.NEAREST)


def tight_box(annotators):
    for key, val in annotators.items():
        if "bounding_box_2d_tight" in key:
            return val
    return None


def pretty_cam(cam):
    return cam.strip("_").replace("World_cameras_", "").replace("_", " ")


# ----------------------------------------------------------------------------- build
def main():
    cams = sorted(d for d in os.listdir(RUN) if os.path.isdir(os.path.join(RUN, d, "object_detection")))
    if not cams:
        raise SystemExit(f"No camera folders with object_detection/ found in {RUN}")

    frames, totals = [], Counter()
    for cam in cams:
        dets = sorted(glob.glob(os.path.join(RUN, cam, "object_detection", "object_detection_*.json")))
        if FRAMES_PER_CAMERA:
            dets = dets[:FRAMES_PER_CAMERA]
        for det_path in dets:
            fid = os.path.splitext(os.path.basename(det_path))[0].split("_")[-1]
            rgb_path = find_one(os.path.join(RUN, cam, "rgb", f"*{fid}.png"))
            if not rgb_path:
                print(f"  skip {cam} {fid}: no rgb")
                continue

            rgb = Image.open(rgb_path)
            W, H = rgb.size
            s = WIDTH / W
            size = (WIDTH, round(H * s))

            objects = []
            for prim, obj in json.load(open(det_path)).get("objects", {}).items():
                cls = obj.get("label", {}).get("class")
                bb = tight_box(obj.get("annotators", {}))
                if not cls or not bb:
                    continue
                x0, y0 = max(0, bb["x_min"]), max(0, bb["y_min"])
                x1, y1 = min(W, bb["x_max"]), min(H, bb["y_max"])
                occ = float(bb.get("occlusionRatio", 0.0))
                if (x1 - x0) < MIN_PX or (y1 - y0) < MIN_PX or occ > MAX_OCCLUSION_EXPORT:
                    continue
                objects.append({
                    "c": cls, "p": prim.replace("/World/full_warehouse/", ""),
                    "x": round(x0 * s, 1), "y": round(y0 * s, 1),
                    "w": round((x1 - x0) * s, 1), "h": round((y1 - y0) * s, 1),
                    "o": round(occ, 3),
                })
                totals[cls] += 1

            views = {"rgb": to_data_uri(rgb.resize(size, Image.LANCZOS), "JPEG")}
            sem = find_one(os.path.join(RUN, cam, "semantic_segmentation", f"*{fid}.png"))
            ins = find_one(os.path.join(RUN, cam, "instance_segmentation*", f"*{fid}.png"))
            if sem:
                views["semantic"] = to_data_uri(load_seg(sem, size), "PNG")
            if ins:
                views["instance"] = to_data_uri(load_seg(ins, size), "PNG")

            frames.append({"cam": pretty_cam(cam), "fid": fid, "w": size[0], "h": size[1],
                           "views": views, "objects": objects, "src": [W, H]})
            print(f"  {pretty_cam(cam)} frame {fid}: {len(objects)} objects, views={list(views)}")

    classes = [c for c in CLASS_COLORS if totals[c]] + sorted(c for c in totals if c not in CLASS_COLORS)
    data = {
        "title": TITLE, "subtitle": SUBTITLE, "author": AUTHOR,
        "classes": classes,
        "colors": {c: CLASS_COLORS.get(c, "#ffffff") for c in classes},
        "totals": dict(totals), "frames": frames,
        "cameras": len(cams),
    }
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "explorer_template.html")).read()
    html = tpl.replace("__TITLE__", TITLE).replace("__DATA__", payload)
    with open(OUT_HTML, "w") as f:
        f.write(html)

    print(f"\nframes: {len(frames)}  objects: {sum(totals.values())}  per class: {dict(totals)}")
    print(f"page ({os.path.getsize(OUT_HTML) / 1e6:.1f} MB) -> {OUT_HTML}")


if __name__ == "__main__":
    main()
