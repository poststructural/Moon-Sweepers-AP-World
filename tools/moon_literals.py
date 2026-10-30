import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "Moon Sweepers" / "MoonSweepers_Data" / "il2cpp_data" / "Metadata" / "global-metadata.dat"
OUT = ROOT / "research" / "moon_literals.txt"

d = META.read_bytes()
base = 62468          # stringLiteralData section
n = 15492             # stringLiterals count (4-byte dataIndex entries at 0x1F4)
offs = list(struct.unpack_from("<%dI" % n, d, 500))
out = []
for i in range(n - 1):
    a = base + offs[i]
    b = base + offs[i + 1]
    out.append(d[a:b].decode("utf-8", "replace"))
OUT.write_text("\n".join(s.replace("\r", "\\r").replace("\n", "\\n") for s in out), encoding="utf-8")
print("wrote", OUT, len(out))
