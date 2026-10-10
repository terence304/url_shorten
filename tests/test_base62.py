"""Tests for base62 encode/decode."""

import pytest

from app.base62 import encode, decode


class TestBase62:
    def test_encode_zero(self):
        assert encode(0) == "0"

    def test_encode_single_digit(self):
        assert encode(9) == "9"
        assert encode(10) == "a"
        assert encode(35) == "z"
        assert encode(36) == "A"
        assert encode(61) == "Z"

    def test_encode_multi_digit(self):
        assert encode(62) == "10"
        assert encode(3843) == "ZZ"  # 61*62 + 61

    def test_decode_single(self):
        assert decode("0") == 0
        assert decode("a") == 10
        assert decode("Z") == 61

    def test_decode_multi(self):
        assert decode("10") == 62
        assert decode("ZZ") == 3843

    def test_round_trip(self):
        for n in [0, 1, 61, 62, 1000, 123456789, 10**12]:
            assert decode(encode(n)) == n

    def test_encode_large_id(self):
        # 100M IDs per day for a year ~ 36.5 billion
        big = 36_500_000_000
        key = encode(big)
        assert len(key) <= 7
        assert decode(key) == big

    def test_encode_negative_raises(self):
        with pytest.raises(ValueError):
            encode(-1)

    def test_key_length_for_max_capacity(self):
        # 62^7 - 1 should be 7 chars
        max_val = 62**7 - 1
        assert len(encode(max_val)) == 7
        assert decode(encode(max_val)) == max_val
