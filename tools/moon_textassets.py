import sys, os, io
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import UnityPy

path = sys.argv[1]
outdir = sys.argv[2] if len(sys.argv) > 2 else None
if outdir:
    os.makedirs(outdir, exist_ok=True)
env = UnityPy.load(path)
n = 0
for o in env.objects:
    if o.type.name != "TextAsset":
        continue
    try:
        t = o.read()
        name = getattr(t, "m_Name", None) or getattr(t, "name", None) or f"path{o.path_id}"
        script = t.m_Script if hasattr(t, "m_Script") else None
        raw = bytes(t.m_Script) if script is not None else b""
        print("====", name, "bytes", len(raw))
        print(raw[:400].decode("utf-8", "replace").replace("\n", "\\n")[:400])
        if outdir:
            safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in str(name))
            with open(os.path.join(outdir, safe + ".txt"), "wb") as f:
                f.write(raw)
        n += 1
        if n > 100:
            break
    except Exception as e:
        print("ERR", o.path_id, type(e).__name__, e)
