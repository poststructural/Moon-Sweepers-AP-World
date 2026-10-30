import sys, struct, collections, os
import UnityPy

path = sys.argv[1]
env = UnityPy.load(path)
objs = {o.path_id: o for o in env.objects}

def pptr(b, off):
    fid = struct.unpack_from("<i", b, off)[0]
    pid = struct.unpack_from("<q", b, off + 4)[0]
    return fid, pid

def read_name(b, off=20):
    # base: PPtr(12) + u8 enabled + pad(3) + PPtr script(12) = 28? check
    ln = struct.unpack_from("<i", b, off)[0]
    if 0 <= ln < 300 and off + 4 + ln <= len(b):
        return b[off+4:off+4+ln].decode("utf-8", "replace")
    return None

mbs = [o for o in env.objects if o.type.name == "MonoBehaviour"]
print("count", len(mbs))
for o in mbs[:6]:
    b = o.get_raw_data()
    print("----", o.path_id, "size", len(b))
    print(b[:64].hex(" "))
    fid, pid = pptr(b, 0)
    print("gameobject", fid, pid)
    print("enabled", b[12])
    sfid, spid = pptr(b, 16)
    print("script", sfid, spid)
    for off in (28, 32):
        print("name@", off, read_name(b, off))
