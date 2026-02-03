
from pathlib import Path
import json, pandas as pd
from datetime import datetime

class FeatureStore:
    def __init__(self, root: Path): self.root=root; root.mkdir(exist_ok=True, parents=True)
    def save(self, name, df, version):
        p=self.root/name/version; p.mkdir(parents=True, exist_ok=True)
        df.to_parquet(p/'data.parquet')
        (p/'manifest.json').write_text(json.dumps({'name':name,'version':version,'created_at':datetime.utcnow().isoformat()},indent=2))
    def load(self, name, version): return pd.read_parquet(self.root/name/version/'data.parquet')
