from __future__ import annotations

import numpy as np
import pytest

from dicom_goruntuleyici.windowing import (
    STANDARD_PRESETS,
    apply_modality_and_voi_lut,
    apply_modality_lut,
    apply_window,
)


def test_modality_lut_applies_rescale_slope_and_intercept():
    raw = np.array([0, 1024, 2048])
    hu = apply_modality_lut(raw, rescale_slope=1.0, rescale_intercept=-1024.0)
    assert list(hu) == [-1024.0, 0.0, 1024.0]


def test_modality_lut_default_is_identity():
    raw = np.array([5, 10, 15])
    assert np.array_equal(apply_modality_lut(raw), raw.astype(np.float64))


# Hand-verified against the exact DICOM PS3.3 C.11.2.1.2.1 LINEAR formula,
# with c=100, w=101 (w-1=100, chosen so the arithmetic is exact by hand):
#   low_threshold  = c - 0.5 - (w-1)/2 = 49.5
#   high_threshold = c - 0.5 + (w-1)/2 = 149.5

def test_value_at_or_below_low_threshold_maps_to_ymin():
    result = apply_window(np.array([49.5, 49.4, 0.0]), window_center=100, window_width=101, y_min=0, y_max=255)
    assert list(result) == [0.0, 0.0, 0.0]


def test_value_above_high_threshold_maps_to_ymax():
    result = apply_window(np.array([149.6, 1000.0]), window_center=100, window_width=101, y_min=0, y_max=255)
    assert list(result) == [255.0, 255.0]


def test_value_at_high_threshold_boundary_is_still_in_linear_region():
    # 149.5 is NOT > high_threshold (149.5), so it takes the linear-formula
    # branch, which for this configuration happens to equal exactly ymax.
    result = apply_window(np.array([149.5]), window_center=100, window_width=101, y_min=0, y_max=255)
    assert result[0] == pytest.approx(255.0, abs=1e-9)


def test_value_at_window_center_matches_hand_computed_asymmetric_value():
    # y = ((100 - 99.5)/100 + 0.5) * 255 = 0.505 * 255 = 128.775 -- NOT
    # 127.5, by the standard's own (documented, intentional) formula.
    result = apply_window(np.array([100.0]), window_center=100, window_width=101, y_min=0, y_max=255)
    assert result[0] == pytest.approx(128.775, rel=1e-9)


def test_window_center_approaches_midpoint_as_width_grows():
    # The center-value asymmetry (0.5/(w-1) of the range) shrinks as w grows.
    narrow = apply_window(np.array([50.0]), window_center=50, window_width=11, y_min=0, y_max=255)
    wide = apply_window(np.array([50.0]), window_center=50, window_width=100001, y_min=0, y_max=255)
    assert abs(narrow[0] - 127.5) > abs(wide[0] - 127.5)
    assert wide[0] == pytest.approx(127.5, abs=0.01)


def test_window_width_below_one_raises():
    with pytest.raises(ValueError):
        apply_window(np.array([0.0]), window_center=0, window_width=0.5)


def test_custom_output_range_is_respected():
    result = apply_window(np.array([49.4, 149.6]), window_center=100, window_width=101, y_min=-1.0, y_max=1.0)
    assert list(result) == [-1.0, 1.0]


def test_full_pipeline_matches_manual_two_step_application():
    raw = np.array([[1000, 1100], [1200, 1300]])
    slope, intercept = 1.0, -1024.0
    wc, ww = 50, 350
    manual = apply_window(apply_modality_lut(raw, slope, intercept), wc, ww)
    full = apply_modality_and_voi_lut(raw, slope, intercept, wc, ww)
    assert np.array_equal(manual, full)


def test_standard_presets_have_positive_width():
    for name, (center, width) in STANDARD_PRESETS.items():
        assert width > 0, f"{name} has non-positive width"


def test_lung_preset_center_is_negative():
    # A well-known qualitative fact: lung window is centered well below
    # zero HU (air/lung parenchyma), unlike bone or soft tissue.
    center, _ = STANDARD_PRESETS["akciger"]
    assert center < 0
