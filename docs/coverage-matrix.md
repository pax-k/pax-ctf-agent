# OmniCTF Coverage Matrix

This file is generated from `config/coverage.json`. Do not edit it directly.

| Category | Subdomain | Owner | Profile | Skill | Tool | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| web | realistic application and API chains | strix | - | ctf-web | - | fixture |
| reverse | native binaries and obfuscation | hexstrike | reverse | ctf-reverse | radare2 | fixture |
| reverse | custom virtual machines | opencode | reverse | ctf-reverse | python3 | fixture |
| reverse | managed and WebAssembly formats | hexstrike | reverse | ctf-reverse | jadx, ilspycmd, wasm2wat | smoke |
| forensics | memory | hexstrike | forensics | ctf-forensics | volatility3 | smoke |
| forensics | network traffic | hexstrike | forensics | ctf-forensics | tshark | fixture |
| forensics | disk and carving | hexstrike | forensics | ctf-forensics | sleuthkit, foremost | smoke |
| forensics | media, documents, and steganography | hexstrike | forensics | ctf-forensics | exiftool, zsteg, ffprobe, oletools | fixture |
| pwn | stack and return-oriented programming | hexstrike | pwn | ctf-pwn | pwndbg, pwntools, ROPgadget | fixture |
| pwn | format strings, heap, and seccomp | hexstrike | pwn | ctf-pwn | pwntools, seccomp-tools | fixture |
| crypto | RSA and classic applied attacks | hexstrike | crypto | ctf-crypto | RsaCtfTool, SageMath | fixture |
| crypto | lattices, constraints, hashes, and symmetric attacks | hexstrike | crypto | ctf-crypto | fpylll, z3, hashcat, xortool | fixture |
| osint | identity pivots | hexstrike | osint | ctf-osint | maigret, sherlock, holehe | fixture |
| osint | DNS, archives, and media verification | hexstrike | osint | ctf-osint | dig, waybackurls, gau, yt-dlp | fixture |
| blockchain | EVM contracts | hexstrike | blockchain | ctf-blockchain | Foundry, Slither, Echidna, Mythril | fixture |
| blockchain | Solana programs | hexstrike | blockchain | ctf-blockchain | Agave, Anchor, SPL Token CLI | fixture |
| misc | media and structured artifacts | hexstrike | misc | ctf-misc | ffmpeg, ImageMagick, jq, sqlite3 | fixture |
| misc | jails and AI or ML | opencode | misc | ctf-ai-ml | Python scientific stack | fixture |
| koth | service patching | opencode | koth | ctf-koth | git, patch, semgrep | fixture |
| koth | flag submission | opencode | koth | ctf-koth | CTF KOTH adapter | fixture |

A listed capability is a repository commitment only at its stated validation level. Live event acceptance remains separate from fixture and smoke evidence.
