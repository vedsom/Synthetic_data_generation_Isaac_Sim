# STEP 7 - workaround: Replicator calls np.save(..., fix_imports=...) which this numpy rejects,
# so distance_to_camera / .npy outputs fail. Run once per Isaac Sim session BEFORE data generation.
import numpy as np
if not getattr(np.save, "_patched", False):
    _orig_save = np.save
    def _save(*args, fix_imports=None, **kwargs):
        return _orig_save(*args, **kwargs)
    _save._patched = True
    np.save = _save
print("np.save patched")
