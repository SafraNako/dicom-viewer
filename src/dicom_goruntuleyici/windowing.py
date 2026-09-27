"""The DICOM Modality LUT + VOI LUT pipeline, implemented exactly as
specified (not approximated):

1. Modality LUT (PS3.3 C.11.1): raw stored pixel values are converted to a
   meaningful physical unit (e.g. Hounsfield Units for CT) via
   HU = stored_value * RescaleSlope + RescaleIntercept.

2. VOI LUT, LINEAR function (PS3.3 C.11.2.1.2.1) -- the exact pseudo-code
   from the standard, with c = Window Center, w = Window Width:

       if x <= c - 0.5 - (w-1)/2:      y = ymin
       elif x >  c - 0.5 + (w-1)/2:    y = ymax
       else:                           y = ((x - (c-0.5)) / (w-1) + 0.5) * (ymax-ymin) + ymin

   This is the DICOM standard's "LINEAR" VOI LUT function (the default when
   VOILUTFunction is absent or "LINEAR"), verified against the standard
   text itself rather than a remembered approximation.
"""

from __future__ import annotations

import numpy as np

# Common radiology window presets (Window Center, Window Width) in Hounsfield
# Units, widely cited in radiology references -- typical/approximate
# conventions, not a fixed part of the DICOM standard itself. See README for
# sources.
STANDARD_PRESETS: dict[str, tuple[float, float]] = {
    "akciger": (-600, 1500),  # lung
    "kemik": (400, 1800),  # bone
    "beyin": (40, 80),  # brain
    "yumusak_doku": (50, 350),  # soft tissue / mediastinum
}


def apply_modality_lut(pixel_array: np.ndarray, rescale_slope: float = 1.0, rescale_intercept: float = 0.0) -> np.ndarray:
    return pixel_array.astype(np.float64) * rescale_slope + rescale_intercept


def apply_window(
    array: np.ndarray, window_center: float, window_width: float, y_min: float = 0.0, y_max: float = 255.0
) -> np.ndarray:
    """Note: per the standard's own "LINEAR" formula, a value exactly at
    window_center does NOT map to exactly the midpoint (y_min+y_max)/2 for
    finite window_width -- it's off by 0.5/(w-1) of the output range. This
    is the DICOM standard's actual defined behavior (there's a separate
    "LINEAR_EXACT" function without this quirk), not a bug here; verified
    against real sample data before being treated as expected rather than
    "fixed" away."""
    if window_width < 1:
        raise ValueError("pencere genişliği (window width) 1'den küçük olamaz")

    c, w = float(window_center), float(window_width)
    low_threshold = c - 0.5 - (w - 1) / 2
    high_threshold = c - 0.5 + (w - 1) / 2

    x = array.astype(np.float64)
    y = np.where(
        x <= low_threshold,
        y_min,
        np.where(
            x > high_threshold,
            y_max,
            ((x - (c - 0.5)) / (w - 1) + 0.5) * (y_max - y_min) + y_min,
        ),
    )
    return y


def apply_modality_and_voi_lut(
    pixel_array: np.ndarray,
    rescale_slope: float,
    rescale_intercept: float,
    window_center: float,
    window_width: float,
    y_min: float = 0.0,
    y_max: float = 255.0,
) -> np.ndarray:
    rescaled = apply_modality_lut(pixel_array, rescale_slope, rescale_intercept)
    return apply_window(rescaled, window_center, window_width, y_min, y_max)
