#!/usr/bin/env python3
"""Patch Pokemon Unbound so EverDrive GBA Pro uses the Fire Red ROM-DB entry.

Usage:
    python3 pkmn_unbound_everdrive_pro_ingameMenu_fix.py "Pokemon - Unbound.gba"

Output:
    patched/Pokemon - Unbound EverDrive CRC.gba
"""

from pathlib import Path
import argparse
import hashlib
import zlib


TARGET_ROMDB_CRC = 0x763AB813
HASH_START = 0xA0
HASH_END = 0x2A0
PATCH_OFFSET = 0xC0
PATCH_BYTES = bytes.fromhex("1d9404d9")
INPUT_SHA256 = "7aa25bbf568f7cfcf6ee1cf2e9e6ff637350b3d0705c2375cabb6baa7d9739f7"
OUTPUT_SHA256 = "403dc0a6e18ab5ca9a5077f186d05d9dcd04ec2b7a3c92b533d113c3ca935442"
DEFAULT_OUTPUT = Path("patched") / "Pokemon - Unbound EverDrive CRC.gba"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Patch Pokemon Unbound for EverDrive GBA Pro in-game menu/savestate DB lookup."
    )
    parser.add_argument("input_gba", type=Path, help="Normal Pokemon Unbound .gba file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output .gba path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    rom = bytearray(args.input_gba.read_bytes())
    if len(rom) < HASH_END:
        raise SystemExit("Input is too small to be a valid GBA ROM")

    input_sha = hashlib.sha256(rom).hexdigest()
    if input_sha != INPUT_SHA256:
        raise SystemExit(
            f"Refusing to patch: input SHA256 is {input_sha}, "
            f"expected {INPUT_SHA256}"
        )

    original_crc = zlib.crc32(rom[HASH_START:HASH_END]) & 0xFFFFFFFF
    if original_crc == TARGET_ROMDB_CRC and rom[PATCH_OFFSET:PATCH_OFFSET + 4] == PATCH_BYTES:
        print("Input already appears patched.")
    else:
        if rom[PATCH_OFFSET:PATCH_OFFSET + 4] != b"\x00\x00\x00\x00":
            raise SystemExit(
                f"Refusing to patch: expected 00000000 at 0x{PATCH_OFFSET:x}, "
                f"found {rom[PATCH_OFFSET:PATCH_OFFSET + 4].hex()}"
            )
        rom[PATCH_OFFSET:PATCH_OFFSET + 4] = PATCH_BYTES

    patched_crc = zlib.crc32(rom[HASH_START:HASH_END]) & 0xFFFFFFFF
    if patched_crc != TARGET_ROMDB_CRC:
        raise SystemExit(f"Patch failed: ROM-DB CRC is 0x{patched_crc:08x}")

    output_sha = hashlib.sha256(rom).hexdigest()
    if output_sha != OUTPUT_SHA256:
        raise SystemExit(
            f"Patch failed: output SHA256 is {output_sha}, "
            f"expected {OUTPUT_SHA256}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(rom)
    print(f"Original ROM-DB CRC: 0x{original_crc:08x}")
    print(f"Patched  ROM-DB CRC: 0x{patched_crc:08x}")
    print(f"Output SHA256: {output_sha}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
"""
this script allows u to enable the ingame state save menu for pkmn unbound for the gba pro (firmware: `edgba-pro-fw-v26.0512.efu`).

after that u can just move your old saves to 
`edgba/gamedata/Pokemon - Unbound EverDrive CRC.gba`

Note: for ingame state menu i use custom shortcut R+B (in everdrive main menu u can press 'select' to change the shortcut for that), cuz the game does not allow u to unbind L

Please buy a fire red cartridge and dump it yourself, never download or share any rom file.
"""
