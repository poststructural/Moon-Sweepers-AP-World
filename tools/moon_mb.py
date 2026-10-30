import sys, collections, os
import UnityPy

path = sys.argv[1]
env = UnityPy.load(path)
mbs = [o for o in env.objects if o.type.name == "MonoBehaviour"]
print("monobehaviours", len(mbs))
ok = 0
for o in mbs:
    try:
        m = o.read()
        cls = type(m).__name__
        name = getattr(m, "m_Name", None)
        script = None
        try:
            sp = m.m_Script
            script = sp.read().m_Name
        except Exception as e:
            script = f"<script err {e}>"
        keys = list(m.__dict__.keys()) if hasattr(m, "__dict__") else []
        print(o.path_id, cls, repr(name)[:60], script, keys[:12])
        ok += 1
    except Exception as e:
        print(o.path_id, "READ-ERR", type(e).__name__, str(e)[:120])
    if ok >= 25:
        break
