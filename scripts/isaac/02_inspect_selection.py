# STEP 2 - inspect the prim(s) selected in the viewport: hierarchy, mesh count, size (read-only).
import omni.usd
from pxr import Usd, UsdGeom

stage = omni.usd.get_context().get_stage()
mpu = UsdGeom.GetStageMetersPerUnit(stage)
bbox = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default", "render"])

for path in omni.usd.get_context().get_selection().get_selected_prim_paths():
    prim = stage.GetPrimAtPath(path)
    print("\n=== SELECTED:", path)
    print("type:", prim.GetTypeName(), "| instanceable:", prim.IsInstanceable())
    p = prim.GetParent()
    while p and str(p.GetPath()) != "/":
        print("  parent:", p.GetName(), f"({p.GetTypeName()})")
        p = p.GetParent()
    meshes = [q for q in Usd.PrimRange(prim, Usd.TraverseInstanceProxies()) if q.IsA(UsdGeom.Mesh)]
    print("meshes inside:", len(meshes))
    size = bbox.ComputeWorldBound(prim).ComputeAlignedRange().GetSize() * mpu
    print(f"size (m): {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f}")
