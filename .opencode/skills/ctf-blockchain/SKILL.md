---
name: ctf-blockchain
description: Analyze authorized EVM and Solana artifacts with local chains, static analyzers, tests, and bounded fuzzing. Use for smart contracts, transactions, programs, ABIs, bytecode, or chain state.
license: Apache-2.0
---

# Analyze a blockchain artifact

Use the optional `hexstrike_lab` MCP backend. Start from supplied source,
bytecode, transaction data, or a local artifact. Identify EVM or Solana before
selecting tools.

For EVM, compile and test with Foundry, inspect calls with Cast, run Slither,
then use Echidna or Mythril with explicit time bounds when static evidence is
not sufficient. For Solana, inspect the program and accounts, build with the
pinned Rust/SBF toolchain, and reproduce behavior against the local validator
before any authorized remote query.

Do not use public funds, production keys, or automatic transaction submission.
Treat a local proof as local evidence. Record the chain, program or contract
identifier, tool version, test seed, and generated output path.
