"""Regression tests for challenge-link encoding.

Challenge tokens are embedded in publicly shared URLs. If the token format
changes, every previously shared link breaks silently. The frozen fixture
below guards against exactly that.
"""
import base64
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import encode_challenge, decode_challenge  # noqa: E402


IDS = ["6612f1a2b3c4d5e6f7a8b9c0", "6612f1a2b3c4d5e6f7a8b9c1"]


def test_roundtrip_with_score():
    token = encode_challenge(IDS, creator_score=83.3)
    assert decode_challenge(token) == (IDS, 83.3)


def test_roundtrip_without_score():
    token = encode_challenge(IDS)
    ids, score = decode_challenge(token)
    assert ids == IDS
    assert score is None


def test_token_is_url_safe():
    """No '+', '/' or '=' - the token travels in a query string."""
    token = encode_challenge(IDS, creator_score=100.0)
    assert not set("+/=") & set(token)


def test_score_is_rounded_to_one_decimal():
    token = encode_challenge(IDS, creator_score=66.6666)
    assert decode_challenge(token)[1] == 66.7


def test_frozen_v1_1_0_token_still_decodes():
    """Frozen fixture: links shared before v1.2.0 must keep working."""
    payload = {"f": IDS, "s": 80.0}
    raw = json.dumps(payload, separators=(",", ":")).encode()
    legacy = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    assert decode_challenge(legacy) == (IDS, 80.0)


@pytest.mark.parametrize("bad", ["", "!!!", "x", "not-a-token", "eyJmIjpb"])
def test_malformed_input_degrades_gracefully(bad):
    """Token arrives from a URL parameter, i.e. untrusted input."""
    assert decode_challenge(bad) == ([], None)


def test_empty_fragment_list_roundtrips():
    assert decode_challenge(encode_challenge([])) == ([], None)
