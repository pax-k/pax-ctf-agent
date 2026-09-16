#!/bin/bash
set -euo pipefail

TARGETARCH=${TARGETARCH:?TARGETARCH is required}
PIP=/usr/local/bin/python3
export PIP_DEFAULT_TIMEOUT=120
export PIP_RETRIES=10
export PIP_RESUME_RETRIES=20
export PIP_CACHE_DIR=/root/.cache/pip
INSTALL_PHASE=${1:-all}

phase_enabled() {
  [ "$INSTALL_PHASE" = all ] || [ "$INSTALL_PHASE" = "$1" ]
}

install_venv() {
  name=$1
  requirements=$2
  "$PIP" -m venv "/opt/ctf-venvs/${name}"
  "/opt/ctf-venvs/${name}/bin/python" -m pip install --upgrade pip
  "/opt/ctf-venvs/${name}/bin/python" -m pip install -r "$requirements"
}

link_venv_commands() {
  name=$1
  shift
  for command_name in "$@"; do
    if [ -x "/opt/ctf-venvs/${name}/bin/${command_name}" ]; then
      ln -sfn "/opt/ctf-venvs/${name}/bin/${command_name}" "/usr/local/bin/${command_name}"
    fi
  done
}

clone_ref() {
  repository=$1
  revision=$2
  destination=$3
  git init -q "$destination"
  git -C "$destination" remote add origin "$repository"
  git -C "$destination" fetch -q --depth 1 origin "$revision"
  git -C "$destination" checkout -q --detach FETCH_HEAD
}

if phase_enabled python-tools; then
install_venv reverse /opt/ctf-requirements/reverse.txt
install_venv reverse-pyinstxtractor /opt/ctf-requirements/reverse-pyinstxtractor.txt
install_venv reverse-uncompyle6 /opt/ctf-requirements/reverse-uncompyle6.txt
install_venv pwn /opt/ctf-requirements/pwn.txt
install_venv forensics /opt/ctf-requirements/forensics.txt
install_venv crypto /opt/ctf-requirements/crypto.txt
install_venv osint /opt/ctf-requirements/osint.txt
install_venv blockchain-audit /opt/ctf-requirements/blockchain-audit.txt
# Mythril 0.24.8 pins Z3 4.12.5. GCC 16 rejects legacy Z3 template
# definitions that Clang still accepts, while Kali's Clang lacks the LTO linker
# plugin expected by that old Z3 build. Build the exact required Z3 release
# with Clang and LTO disabled, then let pip verify it satisfies Mythril.
"$PIP" -m venv /opt/ctf-venvs/blockchain-mythril
/opt/ctf-venvs/blockchain-mythril/bin/python -m pip install --upgrade pip
curl -fsSL -o /tmp/z3-solver.tar.gz \
  https://files.pythonhosted.org/packages/9e/65/4f2b3de02aa1fc95d8d970cd9e0c72526fe916e89d848493413364dcf0ba/z3-solver-4.12.5.0.tar.gz
printf '%s  %s\n' 9a84fcf2c6d39f640cd300e7fbe83dfbe10ef641b5d9134f9b6112237dd619bc /tmp/z3-solver.tar.gz \
  | sha256sum --check --strict
mkdir -p /tmp/z3-solver-src
tar -xzf /tmp/z3-solver.tar.gz -C /tmp/z3-solver-src --strip-components=1
sed -i "s/'Z3_LINK_TIME_OPTIMIZATION' : True/'Z3_LINK_TIME_OPTIMIZATION' : False/" \
  /tmp/z3-solver-src/setup.py
rg -q "'Z3_LINK_TIME_OPTIMIZATION' : False" /tmp/z3-solver-src/setup.py
# New compilers instantiate these old templates and expose member-name typos
# that were dormant in Z3 4.12.5.
sed -i 's/v\.m_matrix\.get(v\.m_row, v\.m_col)/v.m_matrix.get_elem(v.m_row, v.m_col)/' \
  /tmp/z3-solver-src/core/src/math/lp/static_matrix.h
sed -i 's/c\.m_low_bound/c.m_lower_bound/' \
  /tmp/z3-solver-src/core/src/math/lp/column_info.h
sed -i 's/A\.get_value_of_column_cell(col)/A.get_val(col)/' \
  /tmp/z3-solver-src/core/src/math/lp/static_matrix_def.h
rg -q 'v\.m_matrix\.get_elem\(v\.m_row, v\.m_col\)' \
  /tmp/z3-solver-src/core/src/math/lp/static_matrix.h
rg -q 'm_lower_bound == c\.m_lower_bound' \
  /tmp/z3-solver-src/core/src/math/lp/column_info.h
rg -q 'A\.get_val\(col\)' \
  /tmp/z3-solver-src/core/src/math/lp/static_matrix_def.h
CC=clang CXX=clang++ /opt/ctf-venvs/blockchain-mythril/bin/python -m pip install \
  /tmp/z3-solver-src
CC=clang CXX=clang++ /opt/ctf-venvs/blockchain-mythril/bin/python -m pip install \
  -r /opt/ctf-requirements/blockchain-mythril.txt
rm -rf /tmp/z3-solver-src /tmp/z3-solver.tar.gz
install_venv solana-python /opt/ctf-requirements/solana-python.txt
install_venv misc /opt/ctf-requirements/misc.txt
install_venv koth /opt/ctf-requirements/koth.txt

link_venv_commands reverse capa
link_venv_commands reverse-pyinstxtractor pyinstxtractor-ng
link_venv_commands reverse-uncompyle6 uncompyle6
link_venv_commands pwn ROPgadget
link_venv_commands forensics oleid olemeta olevba pdfid.py vol vol.py
link_venv_commands crypto xortool
link_venv_commands osint holehe maigret sherlock yt-dlp
link_venv_commands blockchain-audit crytic-compile slither solc-select
link_venv_commands blockchain-mythril myth
link_venv_commands koth semgrep
fi

if phase_enabled sage; then
case "$TARGETARCH" in
  amd64)
    MICROMAMBA_ARCH=64
    MICROMAMBA_SHA=366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3
    ;;
  arm64)
    MICROMAMBA_ARCH=aarch64
    MICROMAMBA_SHA=9f93b974adcb4d166996af969b6cd371287d1a3e52733704727884d9b74cb7a7
    ;;
  *)
    printf 'unsupported target architecture: %s\n' "$TARGETARCH" >&2
    exit 1
    ;;
esac

curl -fsSL -o /usr/local/bin/micromamba "https://github.com/mamba-org/micromamba-releases/releases/download/2.9.0-0/micromamba-linux-${MICROMAMBA_ARCH}"
printf '%s  %s\n' "$MICROMAMBA_SHA" /usr/local/bin/micromamba | sha256sum --check --strict
chmod 0755 /usr/local/bin/micromamba
micromamba create --yes --root-prefix /opt/micromamba --name sage --channel conda-forge --strict-channel-priority python=3.12 sage=10.9
ln -sfn /opt/micromamba/envs/sage/bin/sage /usr/local/bin/sage
fi

if phase_enabled pwn-support; then
gem install one_gadget --version 2.1.1 --no-document
gem install seccomp-tools --version 1.7.1 --no-document
gem install zsteg --version 0.2.14 --no-document
CARGO_TARGET_DIR=/tmp/pwninit-target cargo install pwninit --version 3.3.3 --locked --root /usr/local
rm -rf /tmp/pwninit-target/*
fi

if phase_enabled pwndbg; then
clone_ref https://github.com/pwndbg/pwndbg.git 0b59278b1189d3a0ff7f6a423c2f1fafa6bb1e9c /opt/pwndbg
(cd /opt/pwndbg && PWNDBG_VENV_PATH=/opt/ctf-venvs/pwndbg HOME=/root ./setup.sh --update)
fi

if phase_enabled research-tools; then
clone_ref https://github.com/RsaCtfTool/RsaCtfTool.git 4475e1dd4431883e73e1418ef8e5d80bc7155467 /opt/RsaCtfTool
"$PIP" -m venv /opt/ctf-venvs/rsactftool
/opt/ctf-venvs/rsactftool/bin/python -m pip install --upgrade pip
/opt/ctf-venvs/rsactftool/bin/python -m pip install -r /opt/RsaCtfTool/requirements.txt
ln -sfn /opt/RsaCtfTool/RsaCtfTool.py /usr/local/bin/RsaCtfTool

GOBIN=/usr/local/bin go install github.com/tomnomnom/waybackurls@8d27cf3e3031de01179e8ba9127e968eb01008e9
GOBIN=/usr/local/bin go install github.com/lc/gau/v2/cmd/gau@8201b9d1febadba98e9cb81e3f253284e8a4a88b
fi

if phase_enabled native-tools; then
clone_ref https://github.com/kimci86/bkcrack.git f7e61bab2dd5976e252d8451527c66a6342b68d2 /opt/bkcrack-src
cmake -S /opt/bkcrack-src -B /opt/bkcrack-build -DCMAKE_BUILD_TYPE=Release
cmake --build /opt/bkcrack-build --parallel "$(nproc)"
install -m 0755 /opt/bkcrack-build/src/cli/bkcrack /usr/local/bin/bkcrack

clone_ref https://github.com/crorvick/outguess.git 9901e486c506893f029fce654f21f59a76a4024d /opt/outguess-src
(cd /opt/outguess-src \
  && CFLAGS=-std=gnu89 ./configure --prefix=/usr/local \
  && make -j"$(nproc)" CFLAGS=-std=gnu89 \
  && make install)

curl -fsSL -o /usr/local/share/cfr.jar https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar
printf '%s  %s\n' f686e8f3ded377d7bc87d216a90e9e9512df4156e75b06c655a16648ae8765b2 /usr/local/share/cfr.jar | sha256sum --check --strict
printf '%s\n' '#!/bin/sh' 'exec java -jar /usr/local/share/cfr.jar "$@"' > /usr/local/bin/cfr
chmod 0755 /usr/local/bin/cfr

curl -fsSL -o /tmp/dotnet-install.sh https://dot.net/v1/dotnet-install.sh
printf '%s  %s\n' 082f7685e156738a1b2e2ed8381a621870d4ce8e8c59278034556f05c186eb2e /tmp/dotnet-install.sh | sha256sum --check --strict
bash /tmp/dotnet-install.sh --version 8.0.425 --install-dir /opt/dotnet --no-path
/opt/dotnet/dotnet tool install ilspycmd --tool-path /opt/ilspy --version 11.0.0.9375
ln -sfn /opt/ilspy/ilspycmd /usr/local/bin/ilspycmd
rm -rf /opt/bkcrack-src /opt/bkcrack-build /opt/outguess-src
fi

if phase_enabled blockchain-evm; then
case "$TARGETARCH" in
  amd64)
    FOUNDRY_ARCH=amd64
    FOUNDRY_SHA=7ca48e6ca3cac1bce1403ca67e5bc1dc3bc1fd818199c9957c7165079c228568
    ECHIDNA_ARCH=x86_64
    ECHIDNA_SHA=436d26cb5af34c6c525812b857ac53f218c7f6ad07d69495ef88bc4cdc85c764
    ;;
  arm64)
    FOUNDRY_ARCH=arm64
    FOUNDRY_SHA=93fc23be26c8a902ca58fe54aa6ca28c880b58af95d052674933161df7928e6d
    ECHIDNA_ARCH=aarch64
    ECHIDNA_SHA=a8853108ac57a43b550c8053dd1cd760fcc5347a9c4c389135fa0ae82a69a221
    ;;
  *)
    printf 'unsupported target architecture: %s\n' "$TARGETARCH" >&2
    exit 1
    ;;
esac

curl -fsSL -o /tmp/foundry.tar.gz "https://github.com/foundry-rs/foundry/releases/download/v1.8.3/foundry_v1.8.3_linux_${FOUNDRY_ARCH}.tar.gz"
printf '%s  %s\n' "$FOUNDRY_SHA" /tmp/foundry.tar.gz | sha256sum --check --strict
tar -xzf /tmp/foundry.tar.gz -C /usr/local/bin

curl -fsSL -o /tmp/echidna.tar.gz "https://github.com/crytic/echidna/releases/download/v2.3.3/echidna-2.3.3-${ECHIDNA_ARCH}-linux.tar.gz"
printf '%s  %s\n' "$ECHIDNA_SHA" /tmp/echidna.tar.gz | sha256sum --check --strict
tar -xzf /tmp/echidna.tar.gz -C /usr/local/bin

/usr/local/bin/solc-select install 0.8.30
/usr/local/bin/solc-select use 0.8.30
fi

if phase_enabled solana-core; then
if [ "$TARGETARCH" = amd64 ]; then
  curl -fsSL -o /tmp/agave.tar.bz2 https://github.com/anza-xyz/agave/releases/download/v4.2.2/solana-release-x86_64-unknown-linux-gnu.tar.bz2
  printf '%s  %s\n' 5fc8684f7430038105fde953d4308ed56addf627f658daa61709f345448247ee /tmp/agave.tar.bz2 | sha256sum --check --strict
  tar -xjf /tmp/agave.tar.bz2 -C /opt
  find /opt/solana-release/bin -maxdepth 1 -type f -exec ln -sfn {} /usr/local/bin/ \;
else
  clone_ref https://github.com/anza-xyz/agave.git v4.2.2 /opt/agave-src
  CARGO_TARGET_DIR=/tmp/agave-target cargo build --manifest-path /opt/agave-src/Cargo.toml --release --locked --bin solana --bin solana-keygen --bin solana-test-validator
  install -m 0755 /tmp/agave-target/release/solana /tmp/agave-target/release/solana-keygen /tmp/agave-target/release/solana-test-validator /usr/local/bin/
  rm -rf /opt/agave-src /tmp/agave-target/*
fi
fi

if phase_enabled solana-anchor; then
if [ "$TARGETARCH" = amd64 ]; then
  curl -fsSL -o /usr/local/bin/anchor https://github.com/coral-xyz/anchor/releases/download/v0.32.2/anchor-0.32.2-x86_64-unknown-linux-gnu
  printf '%s  %s\n' b3cdc15f3db924c2b11a7c16ceff21ad3da239ddde4e53f33df18e52e0461645 /usr/local/bin/anchor | sha256sum --check --strict
  chmod 0755 /usr/local/bin/anchor
else
  clone_ref https://github.com/coral-xyz/anchor.git v0.32.2 /opt/anchor-src
  CARGO_TARGET_DIR=/tmp/anchor-target cargo install --path /opt/anchor-src/cli --locked --root /usr/local
  rm -rf /opt/anchor-src /tmp/anchor-target/*
fi
fi

if phase_enabled solana-spl; then
CARGO_TARGET_DIR=/tmp/spl-target cargo install spl-token-cli --version 5.6.1 --locked --root /usr/local
rm -rf /tmp/spl-target/*
fi

if phase_enabled verify; then
install -m 0755 /opt/ctf-adapter/hashpump_cli.py /usr/local/bin/hashpump

for command_name in file strings readelf objdump r2 analyzeHeadless capa upx jadx apktool d2j-dex2jar cfr ilspycmd wasm2wat uncompyle6 checksec gdb ROPgadget ropper one_gadget pwninit strace ltrace seccomp-tools binwalk vol foremost tshark capinfos fsstat ewfinfo bulk_extractor exiftool steghide zsteg outguess stegsnow mediainfo ffprobe tesseract zbarimg pdfinfo oleid 7z sage RsaCtfTool hashcat john xortool hashpump bkcrack openssl whois dig waybackurls gau maigret sherlock holehe yt-dlp forge cast slither echidna myth solc anchor solana-test-validator spl-token jq sqlite3 identify semgrep; do
  command -v "$command_name" >/dev/null || {
    printf 'required CTF command is unavailable after installation: %s\n' "$command_name" >&2
    exit 1
  }
done
fi
