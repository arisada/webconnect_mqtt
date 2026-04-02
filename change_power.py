#!/usr/bin/env python3

# Copyright 2026 Aris Adamantiadis <aris@badcode.be>
# BSD 2-Clause License

import asyncio
import sys
from porsche_web_mqtt import load_config, parse_args, WebConnectClient


def parse_current_limit(arg: str) -> int:
    try:
        value = int(arg)
    except ValueError:
        print(f"Error: '{arg}' is not an integer", file=sys.stderr)
        sys.exit(1)

    if value < 0 or value > 16:
        print(f"Error: value must be between 0 and 16 inclusive", file=sys.stderr)
        sys.exit(1)

    if 1 <= value <= 3:
        print(f"Rounding {value}A up to 4A (minimum non-zero charging current)")
        value = 4

    return value


async def async_main(current_limit: int):
    config = load_config()
    charger = WebConnectClient(config)
    try:
        await charger.start()
        success = await charger.setHMICurrentLimit(current_limit)
        if success:
            print(f"Current limit set to {current_limit}A")
        else:
            print("Failed to set current limit", file=sys.stderr)
            sys.exit(1)
    finally:
        await charger.stop()


def main():
    parse_args()
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [-v] <current_limit>", file=sys.stderr)
        sys.exit(1)

    current_limit = parse_current_limit(sys.argv[-1])
    asyncio.run(async_main(current_limit))


if __name__ == "__main__":
    main()
