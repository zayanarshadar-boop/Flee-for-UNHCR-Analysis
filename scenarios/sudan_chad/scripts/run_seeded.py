import sys
import runpy
import random
import numpy as np

if len(sys.argv) < 6:
    print(
        "Usage: python run_seeded.py SEED INPUT_DIR DATA_DIR MODE SETTINGS_FILE"
    )
    sys.exit(1)

seed = int(sys.argv[1])

random.seed(seed)
np.random.seed(seed)

print(f"Random seed: {seed}", file=sys.stderr)

sys.argv = [
    "runscripts/run.py",
    sys.argv[2],
    sys.argv[3],
    sys.argv[4],
    sys.argv[5],
]

runpy.run_path("runscripts/run.py", run_name="__main__")
