import joblib
from pathlib import Path
class ModelStore:
  def __init__(s,r): s.r=r; r.mkdir(exist_ok=True, parents=True)
  def save(s,n,m,v): p=s.r/n/v; p.mkdir(parents=True, exist_ok=True); joblib.dump(m,p/'model.joblib')
