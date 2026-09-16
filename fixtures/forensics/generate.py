import os
import struct
import wave
from pathlib import Path


ROOT = Path(os.environ.get("FIXTURE_OUTPUT", "/tmp/omnictf-forensics-fixture"))
ROOT.mkdir(exist_ok=True)

# Deterministic minimal Ethernet/IPv4/UDP packet in a pcap file.
packet = bytes.fromhex(
    "ffffffffffff0200000000010800450000210001000040117cc9"
    "7f0000017f000001c350c351000d00004f4d4e4921"
)
with (ROOT / "fixture.pcap").open("wb") as output:
    output.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    output.write(struct.pack("<IIII", 1, 0, len(packet), len(packet)))
    output.write(packet)

with wave.open(str(ROOT / "fixture.wav"), "wb") as output:
    output.setnchannels(1)
    output.setsampwidth(1)
    output.setframerate(8000)
    output.writeframes(bytes([128, 140, 128, 116]) * 200)

(ROOT / "metadata.txt").write_text("case=omnictf-fixture\nowner=workshop\n", encoding="utf-8")
