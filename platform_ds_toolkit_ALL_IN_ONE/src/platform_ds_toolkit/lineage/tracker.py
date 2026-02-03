import json, datetime
from pathlib import Path
class LineageTracker:
  def __init__(s,r): s.r=r; r.mkdir(exist_ok=True, parents=True)
  def record(s,o,i): (s.r/f'{o}.json').write_text(json.dumps({'output':o,'inputs':i,'ts':datetime.datetime.utcnow().isoformat()},indent=2))
