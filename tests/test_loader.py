from __future__ import annotations

from dicom_goruntuleyici.loader import (
    get_default_window,
    get_pixel_array,
    get_rescale_params,
    load_dataset,
    load_series,
)


def test_load_dataset_reads_real_sample_file(ct_small_path):
    ds = load_dataset(ct_small_path)
    assert ds.Modality == "CT"
    assert ds.Rows == 128
    assert ds.Columns == 128


def test_get_pixel_array_shape_matches_dataset(ct_small_path):
    ds = load_dataset(ct_small_path)
    arr = get_pixel_array(ds)
    assert arr.shape == (128, 128)


def test_get_rescale_params_from_real_ct_sample(ct_small_path):
    ds = load_dataset(ct_small_path)
    slope, intercept = get_rescale_params(ds)
    assert slope == 1.0
    assert intercept == -1024.0


def test_get_rescale_params_defaults_when_absent(mr_small_path):
    ds = load_dataset(mr_small_path)
    if not hasattr(ds, "RescaleSlope"):
        slope, intercept = get_rescale_params(ds)
        assert slope == 1.0
        assert intercept == 0.0


def test_get_default_window_is_none_when_absent(ct_small_path):
    ds = load_dataset(ct_small_path)
    assert get_default_window(ds) is None


def test_load_series_reads_multiple_real_files(tmp_path, ct_small_path, mr_small_path):
    import shutil

    shutil.copy(ct_small_path, tmp_path / "a.dcm")
    shutil.copy(mr_small_path, tmp_path / "b.dcm")
    (tmp_path / "not_dicom.txt").write_text("hello")

    datasets = load_series(str(tmp_path))
    assert len(datasets) == 2
    modalities = {ds.Modality for ds in datasets}
    assert modalities == {"CT", "MR"}


def test_load_series_empty_directory_returns_empty_list(tmp_path):
    assert load_series(str(tmp_path)) == []
