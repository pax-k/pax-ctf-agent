#!/usr/bin/env python3
"""Small CLI for the pinned hashpumpy Python module."""

import argparse

import hashpumpy


def main() -> None:
    parser = argparse.ArgumentParser(description="Perform a hash length extension")
    parser.add_argument("--signature", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--additional", required=True)
    parser.add_argument("--key-length", required=True, type=int)
    args = parser.parse_args()
    digest, message = hashpumpy.hashpump(
        args.signature,
        args.data,
        args.additional,
        args.key_length,
    )
    print(digest)
    print(message.hex())


if __name__ == "__main__":
    main()
