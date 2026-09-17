#!/usr/bin/env python3
"""Start the pinned HexStrike server on localhost only."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


runtime_dir = Path(__file__).resolve().parent.parent / ".hexstrike" / "native"
source_dir = runtime_dir / "hexstrike-ai"
sys.path.insert(0, str(source_dir))

server = importlib.import_module("hexstrike_server")
port = int(os.environ.get("HEXSTRIKE_PORT", "8888"))
server.app.run(host="127.0.0.1", port=port, debug=False)
