# STEP 1 - list object names in the warehouse (read-only). Run in Isaac Sim > Window > Script Editor.
import re
from collections import Counter, defaultdict
import omni.usd
from pxr import Usd, UsdGeom

ROOT = "/World/full_warehouse"
KEYWORDS = ["box", "barrel", "barel", "palette", "pallet", "crate", "bottle", "extinguisher", "cone", "forklift"]

stage = omni.usd.get_context().get_stage()
root = stage.GetPrimAtPath(ROOT)
print("metersPerUnit:", UsdGeom.GetStageMetersPerUnit(stage))

def base_name(n):                      # SM_CardBoxA_03 -> SM_CardBoxA
    return re.sub(r"[_\d]+$", "", n)

hits, example, all_names = defaultdict(Counter), {}, Counter()
for prim in Usd.PrimRange(root):
    name = prim.GetName()
    key = (base_name(name), prim.GetTypeName(), prim.IsInstanceable())
    all_names[key[0]] += 1
    for kw in KEYWORDS:
        if kw in name.lower():
            hits[kw][key] += 1
            example.setdefault((kw, key), str(prim.GetPath()))

for kw in KEYWORDS:
    print(f"\n===== '{kw}' : {sum(hits[kw].values())} prims =====")
    for (pattern, ptype, inst), cnt in hits[kw].most_common(10):
        print(f"{cnt:5d}  {pattern:35s} type={ptype:8s} instanceable={inst}")
        print(f"       e.g. {example[(kw, (pattern, ptype, inst))]}")

print("\n===== 40 most common names overall =====")
for pattern, cnt in all_names.most_common(40):
    print(f"{cnt:5d}  {pattern}")
