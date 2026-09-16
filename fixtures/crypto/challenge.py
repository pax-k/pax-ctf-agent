import os
from pathlib import Path


MESSAGE = b"OMNICTF-FIXTURE"
KEY = b"key"
encoded = bytes(value ^ KEY[index % len(KEY)] for index, value in enumerate(MESSAGE))
Path(os.environ.get("FIXTURE_OUTPUT", "/tmp/omnictf-crypto-xor.bin")).write_bytes(encoded)

# Deliberately small RSA values for a deterministic workshop-only attack.
p, q, e = 10007, 10009, 65537
n = p * q
m = int.from_bytes(b"OK", "big")
print({"n": n, "e": e, "c": pow(m, e, n)})
