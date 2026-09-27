"""Sorting a set of DICOM slices into anatomical order. Real viewers prefer
ImagePositionPatient (the actual 3D position, projected onto the series'
slice-normal direction) since InstanceNumber isn't always reliable or
present; this module tries that first and falls back to InstanceNumber."""

from __future__ import annotations

import numpy as np
import pydicom


def _slice_position(dataset: pydicom.Dataset) -> float | None:
    position = getattr(dataset, "ImagePositionPatient", None)
    orientation = getattr(dataset, "ImageOrientationPatient", None)
    if position is None:
        return None
    position = np.array([float(v) for v in position])
    if orientation is not None:
        orientation = [float(v) for v in orientation]
        row = np.array(orientation[0:3])
        col = np.array(orientation[3:6])
        normal = np.cross(row, col)
        return float(np.dot(position, normal))
    return float(position[2])


def sort_method_used(datasets: list[pydicom.Dataset]) -> str:
    if not datasets:
        return "bos_seri"
    positions = [_slice_position(ds) for ds in datasets]
    if all(p is not None for p in positions):
        return "ImagePositionPatient"
    instance_numbers = [getattr(ds, "InstanceNumber", None) for ds in datasets]
    if all(n is not None for n in instance_numbers):
        return "InstanceNumber"
    return "sırasız (orijinal dosya sırası)"


def sort_series(datasets: list[pydicom.Dataset]) -> list[pydicom.Dataset]:
    positions = [_slice_position(ds) for ds in datasets]
    if all(p is not None for p in positions):
        return [ds for _, ds in sorted(zip(positions, datasets), key=lambda pair: pair[0])]

    instance_numbers = [getattr(ds, "InstanceNumber", None) for ds in datasets]
    if all(n is not None for n in instance_numbers):
        return [ds for _, ds in sorted(zip(instance_numbers, datasets), key=lambda pair: int(pair[0]))]

    return list(datasets)
