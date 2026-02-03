import json
from pathlib import Path
class Registry:
  def __init__(s,p): s.p=p; p.write_text('{}') if not p.exists() else None
  def register(s,n,l): d=json.loads(s.p.read_text()); d[n]=l; s.p.write_text(json.dumps(d,indent=2))
  def resolve(s,n): return json.loads(s.p.read_text())[n]
