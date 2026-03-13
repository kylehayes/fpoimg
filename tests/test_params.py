"""Tests for parameter parsing utilities."""
import pytest
from fpoimg.utils.params import clamp_dimension, MIN_DIMENSION, MAX_DIMENSION


class TestClampDimension:
    """clamp_dimension() should enforce min/max bounds."""

    def test_within_range(self):
        assert clamp_dimension(500) == 500

    def test_below_minimum(self):
        assert clamp_dimension(1) == MIN_DIMENSION

    def test_above_maximum(self):
        assert clamp_dimension(9999) == MAX_DIMENSION

    def test_at_minimum(self):
        assert clamp_dimension(MIN_DIMENSION) == MIN_DIMENSION

    def test_at_maximum(self):
        assert clamp_dimension(MAX_DIMENSION) == MAX_DIMENSION

    def test_zero(self):
        assert clamp_dimension(0) == MIN_DIMENSION

    def test_negative(self):
        assert clamp_dimension(-100) == MIN_DIMENSION
