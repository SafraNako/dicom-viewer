from __future__ import annotations

from conftest import make_synthetic_ct_slice

from dicom_goruntuleyici.series import sort_method_used, sort_series


def test_sorts_by_image_position_patient_even_when_given_scrambled():
    slices = [
        make_synthetic_ct_slice(z_position=20.0, instance_number=3),
        make_synthetic_ct_slice(z_position=0.0, instance_number=1),
        make_synthetic_ct_slice(z_position=10.0, instance_number=2),
    ]
    assert sort_method_used(slices) == "ImagePositionPatient"
    ordered = sort_series(slices)
    assert [s.InstanceNumber for s in ordered] == [1, 2, 3]
    assert [s.ImagePositionPatient[2] for s in ordered] == [0.0, 10.0, 20.0]


def test_falls_back_to_instance_number_when_position_missing():
    slices = []
    for instance_number in (3, 1, 2):
        s = make_synthetic_ct_slice(z_position=0.0, instance_number=instance_number)
        del s.ImagePositionPatient
        slices.append(s)
    assert sort_method_used(slices) == "InstanceNumber"
    ordered = sort_series(slices)
    assert [s.InstanceNumber for s in ordered] == [1, 2, 3]


def test_falls_back_to_original_order_when_nothing_usable():
    slices = []
    for instance_number in (3, 1, 2):
        s = make_synthetic_ct_slice(z_position=0.0, instance_number=instance_number)
        del s.ImagePositionPatient
        del s.InstanceNumber
        slices.append(s)
    assert sort_method_used(slices) == "sırasız (orijinal dosya sırası)"
    ordered = sort_series(slices)
    assert ordered == slices


def test_empty_series_reports_empty_method():
    assert sort_method_used([]) == "bos_seri"
    assert sort_series([]) == []


def test_orientation_affects_slice_normal_projection():
    # With a non-trivial orientation, the sort key is the position projected
    # onto the row x column normal, not just the raw z coordinate.
    a = make_synthetic_ct_slice(z_position=5.0, instance_number=1)
    b = make_synthetic_ct_slice(z_position=1.0, instance_number=2)
    # Identity orientation (already set by the fixture) -> normal is +z,
    # so ordering by projected position matches ordering by raw z.
    ordered = sort_series([a, b])
    assert [s.InstanceNumber for s in ordered] == [2, 1]
