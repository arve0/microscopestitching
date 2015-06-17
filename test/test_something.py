"""
Tests for `microscopestitching`.
"""
import pytest
from microscopestitching import *


def test_stitch():
    "It should stitch side by side images."
    images = [('test/0.png', 0, 0),
              ('test/1.png', 0, 1)]

    stitched, offset = stitch(images)

    assert stitched.shape[1] > 512

    assert offset[0] == 0 # only one row
    assert offset[1] < 0
