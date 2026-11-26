# STEP 3 - report existing semantic labels (old SemanticsAPI + new LabelsAPI) on meshes (read-only).
# Lesson learned: NVIDIA's Simple_Warehouse already ships with 'class' labels (box, pallet, barel, rack, wall...).
from collections import Counter
import omni.usd
from pxr import Usd, UsdGeom

stage = omni.usd.get_context().get_stage()
root = stage.GetPrimAtPath("/World/full_warehouse")
old, new = Counter(), Counter()
for prim in Usd.PrimRange(root):
    if not prim.IsA(UsdGeom.Mesh):
        continue
    for attr in prim.GetAttributes():
        n = attr.GetName()
        if n.startswith("semantic:") and n.endswith(":params:semanticType"):
            data = prim.GetAttribute(n.replace("semanticType", "semanticData"))
            old[(attr.Get(), data.Get() if data else None)] += 1
        elif n.startswith("semantics:labels:"):
            for v in attr.Get() or []:
                new[(n.split(":")[-1], v)] += 1
print("=== OLD-format labels (type, value) ===")
for k, c in old.most_common():
    print(f"{c:6d}  {k}")
print("\n=== NEW-format labels (type, value) ===")
for k, c in new.most_common():
    print(f"{c:6d}  {k}")
