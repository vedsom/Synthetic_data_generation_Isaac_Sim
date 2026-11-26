# STEP 4 (optional) - add 'class' labels to meshes by name pattern (new LabelsAPI). MODE="remove" undoes it.
# Not needed for Simple_Warehouse (already labelled) - useful for scenes without labels.
from collections import Counter
import omni.usd
from pxr import Usd, UsdGeom, UsdSemantics

ROOT, SEM_TYPE, MODE = "/World/full_warehouse", "class", "apply"
RULES = [("cardboard_box", "cardbox"), ("pallet", "palette"), ("barrel", "barelplastic"),
         ("bottle", "bottleplastic"), ("plastic_crate", "crateplastic")]

stage = omni.usd.get_context().get_stage()
counts = Counter()
for prim in Usd.PrimRange(stage.GetPrimAtPath(ROOT)):
    if not prim.IsA(UsdGeom.Mesh):
        continue
    cls = next((c for c, key in RULES if key in prim.GetName().lower()), None)
    if not cls:
        continue
    if MODE == "apply":
        UsdSemantics.LabelsAPI.Apply(prim, SEM_TYPE).CreateLabelsAttr().Set([cls])
    else:
        attr = UsdSemantics.LabelsAPI(prim, SEM_TYPE).GetLabelsAttr()
        if attr:
            prim.RemoveProperty(attr.GetName())
        prim.RemoveAppliedSchema(f"SemanticsLabelsAPI:{SEM_TYPE}")
    counts[cls] += 1
print(MODE, dict(counts))
