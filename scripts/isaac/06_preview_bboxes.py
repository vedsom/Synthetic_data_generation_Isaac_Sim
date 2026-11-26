# STEP 6 - render ONE frame from a camera and draw Replicator ground-truth 2D boxes (quick check).
import asyncio
from collections import Counter
import omni.replicator.core as rep
from PIL import Image, ImageDraw

CAM, OUT = "/World/cameras/Camera_1", "/tmp/preview_Camera_1.png"
KEEP = "class:box|pallet|barel|crate|bottle|forklift"
COLORS = {"box": "yellow", "pallet": "cyan", "barel": "blue", "crate": "lime", "bottle": "magenta", "forklift": "red"}

async def preview():
    from omni.syntheticdata import SyntheticData
    SyntheticData.Get().set_instance_mapping_semantic_filter(KEEP)
    rp = rep.create.render_product(CAM, (1280, 720))
    rgb = rep.AnnotatorRegistry.get_annotator("rgb"); rgb.attach(rp)
    bbox = rep.AnnotatorRegistry.get_annotator("bounding_box_2d_tight"); bbox.attach(rp)
    await rep.orchestrator.step_async(rt_subframes=8)
    img = Image.fromarray(rgb.get_data()[:, :, :3]); data = bbox.get_data()
    id2lbl, draw, counts = data["info"]["idToLabels"], ImageDraw.Draw(img), Counter()
    for b in data["data"]:
        sid = int(b["semanticId"]); lbl = id2lbl.get(str(sid), id2lbl.get(sid, {}))
        cls = lbl.get("class", "?") if isinstance(lbl, dict) else str(lbl)
        counts[cls] += 1; c = COLORS.get(cls, "white")
        draw.rectangle([b["x_min"], b["y_min"], b["x_max"], b["y_max"]], outline=c, width=2)
        draw.text((b["x_min"] + 3, b["y_min"] + 2), cls, fill=c)
    img.save(OUT)
    rgb.detach(); bbox.detach(); rp.destroy()
    SyntheticData.Get().set_instance_mapping_semantic_filter("*:*")
    print(dict(counts), "->", OUT)

asyncio.ensure_future(preview())
