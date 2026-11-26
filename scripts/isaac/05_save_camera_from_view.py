# STEP 5 - save the current viewport view as a camera under /World/cameras.
import omni.usd
from omni.kit.viewport.utility import get_active_viewport
from pxr import Usd, UsdGeom

NAME, PARENT = "Camera_1", "/World/cameras"     # <- change NAME for each camera
stage = omni.usd.get_context().get_stage()
vp = get_active_viewport()
if str(vp.camera_path).startswith(PARENT):
    raise RuntimeError("You are looking THROUGH a saved camera - switch back to Perspective first")
src = UsdGeom.Camera(stage.GetPrimAtPath(vp.camera_path))
UsdGeom.Xform.Define(stage, PARENT)
cam = UsdGeom.Camera.Define(stage, f"{PARENT}/{NAME}")
for a in ["FocalLength", "HorizontalAperture", "VerticalAperture", "ClippingRange"]:
    getattr(cam, f"Create{a}Attr")(getattr(src, f"Get{a}Attr")().Get())
world = UsdGeom.Xformable(src).ComputeLocalToWorldTransform(Usd.TimeCode.Default())
xf = UsdGeom.Xformable(cam); xf.ClearXformOpOrder(); xf.AddTransformOp().Set(world)
print("saved", NAME, "at", world.ExtractTranslation())
