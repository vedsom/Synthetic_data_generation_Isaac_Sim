# STEP 8 - write a valid Actor SDG (isaacsim.replicator.agent) config with Python, then load it in the Actor SDG tab.
import os, yaml

BASE = "/media/omv-200/New Volume2/Abhishek/synthetic_data_gen"     # <- your project folder
CFG = os.path.join(BASE, "minimal.yaml")
config = {"isaacsim.replicator.agent": {
    "version": "1.6.0", "seed": 3533396751, "simulation_duration": 10.0,
    "environment": {"base_stage_asset_path": os.path.join(BASE, "warehouse.usd")},
    # NOTE: no 'sensor' section - an empty sensor.root_prim_path fails validation
    "replicator": {"writers": {"IRABasicWriter": {
        "output_dir": os.path.join(BASE, "IRA_Output_3"),
        # NOTE: use semantic_filter_predicate OR semantic_types, never both
        "semantic_filter_predicate": "class:box|pallet|barel|crate|bottle|forklift;id:*",
        "rgb": True, "semantic_segmentation": True, "instance_segmentation": True,
        "distance_to_camera": True, "camera_params": True,
        "bounding_box_2d_tight": True, "bounding_box_3d": True,
        # NOTE: object_info_* fills the object_detection/ folder (the per-object boxes)
        "object_info_bounding_box_2d_tight": True,
        "object_info_bounding_box_2d_loose": False, "object_info_bounding_box_3d": False,
        "start_frame": 0, "end_frame": 8,
        "sensor_prim_list": [f"/World/cameras/Camera_{i}" for i in range(1, 6)],
    }}},
}}
with open(CFG, "w") as f:
    yaml.safe_dump(config, f, sort_keys=False)
print(open(CFG).read())
