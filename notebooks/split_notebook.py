import json

SRC = "02_pull_stats.ipynb"
nb = json.load(open(SRC, encoding="utf-8"))
cells = nb["cells"]

base = """import re, unicodedata
import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error
"""
pull = """import os, re, time, glob, unicodedata
import numpy as np
import pandas as pd
import requests
from pybaseball import (cache, bwar_bat, bwar_pitch, chadwick_register,
                        statcast_batter_percentile_ranks,
                        statcast_pitcher_percentile_ranks)
cache.enable()
"""
bench = "import glob\n" + base

plans = {
    "02_data_build.ipynb":       (pull,  [0,1,2,3,4,5,6,7,12,13,19,20,21,30,37]),
    "03_models.ipynb":           (base,  [8,9,10,11,14,15,22,23,24]),
    "04_benchmark.ipynb":        (bench, [31,32,33,34,35,36]),
    "05_2027_projections.ipynb": (base,  [16,17,18,43,39,40,41,42,44,45]),
}

for name, (header, idx) in plans.items():
    new = json.loads(json.dumps(nb))
    head = {"cell_type": "code", "metadata": {}, "outputs": [],
            "execution_count": None, "source": header.splitlines(keepends=True)}
    body = []
    for i in idx:
        c = json.loads(json.dumps(cells[i]))
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None
        body.append(c)
    new["cells"] = [head] + body
    json.dump(new, open(name, "w", encoding="utf-8"), indent=1)
    print("wrote", name, len(body), "cells")
    