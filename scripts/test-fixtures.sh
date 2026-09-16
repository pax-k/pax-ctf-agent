#!/bin/sh
set -eu

category=${1:-all}
fixture_tmp=$(mktemp -d /tmp/omnictf-fixtures.XXXXXX)
trap 'rm -rf "$fixture_tmp"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

run_reverse() {
  cc -O0 -s fixtures/reverse/native/check.c -o "${fixture_tmp}/reverse-check"
  "${fixture_tmp}/reverse-check" delta >/dev/null \
    || { printf '%s\n' 'reverse native fixture rejected its known input' >&2; return 1; }
  test "$(python3 fixtures/reverse/vm/challenge.py)" = 43
}

run_web() {
  python3 -m py_compile fixtures/web/app.py
}

run_forensics() {
  FIXTURE_OUTPUT="${fixture_tmp}/forensics" python3 fixtures/forensics/generate.py
  test -s "${fixture_tmp}/forensics/fixture.pcap"
  test -s "${fixture_tmp}/forensics/fixture.wav"
}

run_pwn() {
  linker_flags=
  if [ "$(uname -s)" = Linux ]; then
    linker_flags='-z execstack'
  fi
  for source in fixtures/pwn/*.c; do
    # shellcheck disable=SC2086
    cc -O0 -fno-stack-protector $linker_flags "$source" -o "${fixture_tmp}/$(basename "$source" .c)"
  done
}

run_crypto() {
  FIXTURE_OUTPUT="${fixture_tmp}/xor.bin" python3 fixtures/crypto/challenge.py >/dev/null
  test -s "${fixture_tmp}/xor.bin"
}

run_osint() {
  python3 -m json.tool fixtures/osint/dossier.json >/dev/null
}

run_blockchain() {
  grep -q 'msg.sender.call' fixtures/blockchain/evm/src/Vault.sol
  grep -q 'try_borrow_mut_data' fixtures/blockchain/solana/src/lib.rs
}

run_misc() {
  python3 -m py_compile fixtures/misc/jail.py
  python3 -m json.tool fixtures/misc/model.json >/dev/null
}

run_koth() {
  cp -R fixtures/koth/service "${fixture_tmp}/service"
  git -C "${fixture_tmp}/service" init -q
  git -C "${fixture_tmp}/service" add .
  git -C "${fixture_tmp}/service" -c user.name=fixture -c user.email=fixture@example.invalid commit -qm baseline
  git -C "${fixture_tmp}/service" apply --check "$(pwd)/fixtures/koth/fix.patch"
  python3 -m py_compile fixtures/koth/score_server.py
}

if [ "$category" = all ]; then
  for selected in reverse web forensics pwn crypto osint blockchain misc koth; do
    "run_${selected}"
  done
else
  "run_${category}"
fi

printf '%s\n' "fixture tests passed: ${category}"
