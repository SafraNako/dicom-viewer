"""DICOM file I/O via pydicom (the established, community-maintained DICOM
library) -- the DICOM standard itself runs to thousands of pages across
dozens of transfer syntaxes and compression schemes; parsing it from
scratch would be reinventing a well-tested wheel badly. This module wraps
pydicom for loading; windowing.py implements the actual image-processing
pipeline this tool is responsible for getting right.
"""

from __future__ import annotations

from pathlib import Path

import pydicom


def load_dataset(path: str) -> pydicom.Dataset:
    return pydicom.dcmread(path)


def get_pixel_array(dataset: pydicom.Dataset):
    return dataset.pixel_array


def get_rescale_params(dataset: pydicom.Dataset) -> tuple[float, float]:
    slope = float(getattr(dataset, "RescaleSlope", 1.0))
    intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
    return slope, intercept


def get_default_window(dataset: pydicom.Dataset) -> tuple[float, float] | None:
    """Returns the DICOM file's own recommended (WindowCenter, WindowWidth),
    if present. Some files store multiple values (multi-frame or
    multi-VOI); the first is used, matching common viewer behavior."""
    center = getattr(dataset, "WindowCenter", None)
    width = getattr(dataset, "WindowWidth", None)
    if center is None or width is None:
        return None
    if hasattr(center, "__iter__") and not isinstance(center, str):
        center = center[0]
    if hasattr(width, "__iter__") and not isinstance(width, str):
        width = width[0]
    return float(center), float(width)


def load_series(directory: str) -> list[pydicom.Dataset]:
    """Loads every DICOM file directly inside `directory` (non-recursive)."""
    datasets = []
    for path in sorted(Path(directory).iterdir()):
        if path.is_file():
            try:
                datasets.append(pydicom.dcmread(str(path)))
            except pydicom.errors.InvalidDicomError:
                continue
    return datasets
