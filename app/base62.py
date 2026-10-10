"""Base62 encode / decode for short URL key generation."""

from __future__ import annotations

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)  # 62


def encode(num: int) -> str:
    """Encode a positive integer to a base62 string."""
    if num < 0:
        raise ValueError("Cannot encode negative numbers")
    if num == 0:
        return ALPHABET[0]
    chars: list[str] = []
    while num:
        num, remainder = divmod(num, BASE)
        chars.append(ALPHABET[remainder])
    return "".join(reversed(chars))


def decode(s: str) -> int:
    """Decode a base62 string back to a positive integer."""
    num = 0
    for char in s:
        idx = ALPHABET.index(char)
        num = num * BASE + idx
    return num
