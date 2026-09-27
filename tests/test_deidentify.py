from __future__ import annotations

from dicom_goruntuleyici.deidentify import IDENTIFYING_TAG_KEYWORDS, deidentify, find_identifying_data
from dicom_goruntuleyici.loader import load_dataset


def test_finds_identifying_tags_in_real_sample(ct_small_path):
    ds = load_dataset(ct_small_path)
    found = find_identifying_data(ds)
    assert "PatientName" in found
    assert "PatientID" in found
    assert found["PatientName"] == str(ds.PatientName)


def test_deidentify_removes_all_identifying_tags(ct_small_path):
    ds = load_dataset(ct_small_path)
    cleaned = deidentify(ds)
    remaining = find_identifying_data(cleaned)
    assert remaining == {}


def test_deidentify_does_not_mutate_the_original(ct_small_path):
    ds = load_dataset(ct_small_path)
    original_name = str(ds.PatientName)
    deidentify(ds)
    assert str(ds.PatientName) == original_name
    assert "PatientName" in find_identifying_data(ds)


def test_deidentify_preserves_pixel_data_and_clinical_fields(ct_small_path):
    ds = load_dataset(ct_small_path)
    cleaned = deidentify(ds)
    assert cleaned.Modality == ds.Modality
    assert cleaned.Rows == ds.Rows
    assert cleaned.pixel_array.shape == ds.pixel_array.shape
    import numpy as np
    assert np.array_equal(cleaned.pixel_array, ds.pixel_array)


def test_find_identifying_data_on_dataset_with_no_identifying_tags():
    from pydicom.dataset import Dataset

    empty = Dataset()
    empty.Modality = "CT"
    assert find_identifying_data(empty) == {}


def test_identifying_tag_list_is_nonempty_and_has_no_duplicates():
    assert len(IDENTIFYING_TAG_KEYWORDS) > 0
    assert len(IDENTIFYING_TAG_KEYWORDS) == len(set(IDENTIFYING_TAG_KEYWORDS))
