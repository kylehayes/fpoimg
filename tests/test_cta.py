"""Tests for CTA (Call To Action) display logic."""
import pytest
from unittest.mock import patch
from main import should_show_cta, _CTA_MIN_WIDTH, _CTA_MIN_HEIGHT


class TestShouldShowCta:
    """should_show_cta() gates whether the support QR code appears."""

    def test_nosupport_flag_disables(self):
        """nosupport=True should always return False."""
        with patch("main._CTA_FREQUENCY", 1):
            assert should_show_cta(500, 500, nosupport=True) is False

    def test_frequency_zero_disables(self):
        """_CTA_FREQUENCY=0 means CTA is globally off."""
        with patch("main._CTA_FREQUENCY", 0):
            assert should_show_cta(500, 500, nosupport=False) is False

    def test_image_too_narrow(self):
        """Images below minimum width should not show CTA."""
        with patch("main._CTA_FREQUENCY", 1):
            assert should_show_cta(_CTA_MIN_WIDTH - 1, 500, nosupport=False) is False

    def test_image_too_short(self):
        """Images below minimum height should not show CTA."""
        with patch("main._CTA_FREQUENCY", 1):
            assert should_show_cta(500, _CTA_MIN_HEIGHT - 1, nosupport=False) is False

    def test_shows_when_conditions_met_and_rng_hits(self):
        """Should return True when all conditions are met and RNG rolls 1."""
        with patch("main._CTA_FREQUENCY", 5), \
             patch("main.random.randint", return_value=1):
            assert should_show_cta(500, 500, nosupport=False) is True

    def test_hides_when_rng_misses(self):
        """Should return False when RNG doesn't roll 1."""
        with patch("main._CTA_FREQUENCY", 5), \
             patch("main.random.randint", return_value=3):
            assert should_show_cta(500, 500, nosupport=False) is False

    def test_frequency_one_always_shows(self):
        """_CTA_FREQUENCY=1 means always show (1 in 1 chance)."""
        with patch("main._CTA_FREQUENCY", 1):
            # randint(1, 1) always returns 1
            assert should_show_cta(500, 500, nosupport=False) is True

    def test_exact_minimum_dimensions(self):
        """Exactly at minimum dimensions should be eligible."""
        with patch("main._CTA_FREQUENCY", 1):
            assert should_show_cta(_CTA_MIN_WIDTH, _CTA_MIN_HEIGHT, nosupport=False) is True
