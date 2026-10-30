import sys, struct, collections, os, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import UnityPy

def pptr(b, off):
    return struct.unpack_from("<i", b, off)[0], struct.unpack_from("<q", b, off + 4)[0]

def read_str(b, off):
    if off + 4 > len(b):
        return None
    ln = struct.unpack_from("<i", b, off)[0]
    if 0 <= ln < 500 and off + 4 + ln <= len(b):
        return b[off+4:off+4+ln].decode("utf-8", "replace")
    return None

def mb_name(b):
    # base MonoBehaviour: PPtr go (12), enabled u8 + pad 3, PPtr script (12), string name
    if len(b) >= 32:
        return read_str(b, 28)
    return None

def script_name(obj):
    try:
        s = obj.read()
        return getattr(s, "m_Name", None)
    except Exception:
        try:
            b = obj.get_raw_data()
            return read_str(b, 0) or read_str(b, 4)
        except Exception:
            return None

def run(path, out):
    print(f"\n===== {os.path.basename(path)}", file=out)
    env = UnityPy.load(path)
    print("objects", len(env.objects), file=out)
    by_type = collections.Counter(o.type.name for o in env.objects)
    print("types", dict(by_type.most_common(25)), file=out)

    scripts = {}
    for o in env.objects:
        if o.type.name == "MonoScript":
            n = script_name(o)
            if n:
                scripts[o.path_id] = n

    groups = collections.defaultdict(list)
    no_name = 0
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        b = o.get_raw_data()
        nm = mb_name(b)
        sfid, spid = pptr(b, 16) if len(b) >= 28 else (0, 0)
        sname = scripts.get(spid) if sfid == 1 else f"ext:{sfid}:{spid}"
        if nm:
            groups[sname].append(nm)
        else:
            no_name += 1
    print("monobehaviours with name", sum(len(v) for v in groups.values()), "no name", no_name, file=out)
    print("distinct scripts with named instances", len(groups), file=out)
    for sname, names in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        uniq = sorted(set(names))
        print(f"\n## {sname}  instances={len(names)} unique_names={len(uniq)}", file=out)
        for n in uniq[:40]:
            print("   ", n, file=out)
        if len(uniq) > 40:
            print(f"    ... {len(uniq)-40} more", file=out)

    try:
        print("\ncontainer entries", len(env.container), file=out)
        for i, (k, v) in enumerate(env.container.items()):
            if i >= 200: break
            print("  ", k, "->", v.type.name, file=out)
    except Exception as e:
        print("container error", e, file=out)

if __name__ == "__main__":
    outp = sys.argv[1]
    with open(outp, "w", encoding="utf-8") as f:
        for p in sys.argv[2:]:
            try:
                run(p, f)
            except Exception as e:
                print("FILE ERROR", p, type(e).__name__, e, file=f)
