from __future__ import annotations

import numpy as np

from dicom_goruntuleyici.export import save_comparison_grid, save_image, save_montage


def test_save_image_writes_nonempty_png(tmp_path):
    path = tmp_path / "img.png"
    arr = np.random.randint(0, 256, (32, 32))
    save_image(str(path), arr, title="test")
    assert path.exists() and path.stat().st_size > 0


def test_save_comparison_grid_writes_nonempty_png(tmp_path):
    path = tmp_path / "grid.png"
    images = {f"preset {i}": np.random.randint(0, 256, (16, 16)) for i in range(4)}
    save_comparison_grid(str(path), images, suptitle="test")
    assert path.exists() and path.stat().st_size > 0


def test_save_montage_writes_nonempty_png(tmp_path):
    path = tmp_path / "montage.png"
    slices = [np.random.randint(0, 256, (16, 16)) for _ in range(5)]
    save_montage(str(path), slices, suptitle="test")
    assert path.exists() and path.stat().st_size > 0


def test_save_montage_handles_single_slice(tmp_path):
    path = tmp_path / "single.png"
    save_montage(str(path), [np.zeros((8, 8))], suptitle="test")
    assert path.exists() and path.stat().st_size > 0
