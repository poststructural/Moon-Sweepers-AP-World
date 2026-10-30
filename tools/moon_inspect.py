import sys, collections, json, os
import UnityPy

def summary(path):
    env = UnityPy.load(path)
    types = collections.Counter(o.type.name for o in env.objects)
    print(f"=== {os.path.basename(path)} objects={len(env.objects)}")
    for k, v in types.most_common(40):
        print(f"  {k}: {v}")
    return env

if __name__ == "__main__":
    for p in sys.argv[1:]:
        env = summary(p)
        try:
            print("container entries:", len(env.container))
            for i, (k, v) in enumerate(env.container.items()):
                if i >= 15: break
                print("  ", k, "->", v.type.name)
        except Exception as e:
            print("container error", e)
