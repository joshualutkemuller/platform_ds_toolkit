from pathlib import Path
import shutil, json, hashlib, datetime

def archive_file(src, root): root=Path(root); root.mkdir(exist_ok=True); d=root/datetime.datetime.now().strftime('%Y%m%d_%H%M%S'); d.mkdir(); f=Path(src); c=d/f.name; shutil.copy2(f,c); h=hashlib.sha256(c.read_bytes()).hexdigest(); (d/'manifest.json').write_text(json.dumps({'file':f.name,'sha256':h},indent=2)); return d
