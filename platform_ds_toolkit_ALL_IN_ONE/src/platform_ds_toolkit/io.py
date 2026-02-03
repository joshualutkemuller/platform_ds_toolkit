import pandas as pd
from pathlib import Path

def read(p, **k): return pd.read_parquet(p) if str(p).endswith('.parquet') else pd.read_csv(p, **k)
