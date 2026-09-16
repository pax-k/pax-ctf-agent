# Third-Party Material

Project-authored code is Apache-2.0. Each integrated or vendored component keeps
its own license. The table records source declarations, not a complete license
review of a built image.

| Material | Upstream | Revision | Declared license | Distribution form |
| --- | --- | --- | --- | --- |
| Strix invocation skill | `usestrix/strix` | `2dadbb748a09053463a66abb773e710fa49d2a35` | Apache-2.0 | Vendored skill file |
| Mobile and CI/CD skills | `securityfortech/hacking-skills` | `0aa49b400dc0e093947e393c45c09821bb8d45f4` | Individual files declare MIT | Vendored skill files with local safety additions |
| CTF category skills | `ljagiello/ctf-skills` | `c332c7be1b27cb64639a20124ac55ba916adef92` | MIT | Selected vendored skill trees with local safety additions |
| HexStrike AI | `0x4m4/hexstrike-ai` | `d689933ff579d839c676c82b231f8e98326c5f04` | MIT | Fetched during image build |
| libc-database | `niklasb/libc-database` | `b7e948f7324cde8ac5cdb26bc4d58fbeeb1fbb5c` | MIT | Fetched during image build |
| pwndbg | `pwndbg/pwndbg` | `0b59278b1189d3a0ff7f6a423c2f1fafa6bb1e9c` | MIT | Fetched during image build |
| RsaCtfTool | `RsaCtfTool/RsaCtfTool` | `4475e1dd4431883e73e1418ef8e5d80bc7155467` | See upstream `LICENSE.txt` | Fetched during image build |
| bkcrack | `kimci86/bkcrack` | `f7e61bab2dd5976e252d8451527c66a6342b68d2` | See upstream `license.txt` | Fetched and compiled during image build |
| OutGuess | `crorvick/outguess` | `9901e486c506893f029fce654f21f59a76a4024d` | Upstream source terms | Fetched and compiled during image build |
| waybackurls | `tomnomnom/waybackurls` | `8d27cf3e3031de01179e8ba9127e968eb01008e9` | MIT | Built during image build |
| gau | `lc/gau` | `8201b9d1febadba98e9cb81e3f253284e8a4a88b` | MIT | Built during image build |
| Foundry | `foundry-rs/foundry` | `v1.8.3` | Apache-2.0 or MIT | Verified release binaries |
| Echidna | `crytic/echidna` | `v2.3.3` | AGPL-3.0 | Verified release binaries |
| Agave | `anza-xyz/agave` | `v4.2.2` | Apache-2.0 | Verified AMD64 release or ARM64 source build |
| Anchor | `coral-xyz/anchor` | `v0.32.2` | Apache-2.0 | Verified AMD64 release or ARM64 source build |

The image also distributes Kali packages, Python packages, Ruby gems, Rust
crates, Go modules, .NET tools, and their transitive dependencies. Their
licenses are not replaced by the repository license. The build records exact
resolved package versions. CI is configured to generate an SPDX SBOM and a
Trivy vulnerability report for each native architecture. It does not perform
a separate license-compliance gate.

The selected CTF skills retain their upstream MIT license at
`.opencode/skills/_licenses/ctf-skills-MIT.txt`. The broad upstream
`solve-challenge` skill and installer are not distributed.

Local edits in the CTF Web and Forensics trees replace credential-like teaching
values with runtime variables or synthetic data. A SQLmap example uses its
long `--url` option to avoid a scanner match across separate commands. These
changes preserve the tool examples without excluding files or secret rules
from scanning. The updated local hashes are recorded in the skill lock.

## Vendored skill provenance

All installed skill directories are recorded in
[`config/skills.lock.json`](./config/skills.lock.json). Content hashes cover the
local files, including any local safety additions. A recorded review state
describes that entry; it is not a security certification of every payload in
the skill.

The Strix skill matches its pinned upstream file. Its upstream license is
[Apache-2.0](https://github.com/usestrix/strix/blob/2dadbb748a09053463a66abb773e710fa49d2a35/LICENSE).

## Open source-publication item

The twelve mobile and CI/CD skills from
[`securityfortech/hacking-skills`](https://github.com/securityfortech/hacking-skills/tree/0aa49b400dc0e093947e393c45c09821bb8d45f4)
each declare `license: MIT`. The pinned upstream tree has no `LICENSE` or
`NOTICE` file. The seven mobile files are unchanged. The five CI/CD files
contain local safety edits.

Before public redistribution, resolve the missing upstream license text and
copyright attribution for those files. Obtain the applicable notice or choose
an authorized replacement or removal. Do not invent a copyright holder or
silently relabel these files as Apache-2.0. This remains an open publication
review item.

Publishing a built container is a separate decision. Review the licenses and
source-distribution obligations of its resolved contents, including Echidna,
before uploading an image. The existing CI does not publish images.
