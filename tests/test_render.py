from __future__ import annotations

from dicom_goruntuleyici.render import (
    format_dataset_info,
    format_deidentify_result,
    format_identifying_tags,
    format_series_summary,
)


def test_format_dataset_info_includes_key_fields():
    text = format_dataset_info(
        modality="CT", rows=128, columns=128, rescale_slope=1.0, rescale_intercept=-1024.0,
        default_window=None, pixel_spacing=["0.66", "0.66"],
    )
    assert "CT" in text
    assert "128" in text
    assert "-1024.0" in text
    assert "yok" in text  # no default window present


def test_format_dataset_info_shows_default_window_when_present():
    text = format_dataset_info(
        modality="CT", rows=128, columns=128, rescale_slope=1.0, rescale_intercept=0.0,
        default_window=(40, 80), pixel_spacing=None,
    )
    assert "WC=40" in text
    assert "WW=80" in text


def test_format_identifying_tags_hides_values_by_default():
    text = format_identifying_tags({"PatientName": "Gizli Isim"}, show_values=False)
    assert "Gizli Isim" not in text
    assert "PatientName" in text


def test_format_identifying_tags_shows_values_when_requested():
    text = format_identifying_tags({"PatientName": "Gizli Isim"}, show_values=True)
    assert "Gizli Isim" in text


def test_format_identifying_tags_empty_case():
    text = format_identifying_tags({}, show_values=False)
    assert "bulunamadı" in text


def test_format_deidentify_result_reports_count_and_path():
    text = format_deidentify_result(removed_count=6, output_path="/tmp/out.dcm")
    assert "6" in text
    assert "/tmp/out.dcm" in text


def test_format_series_summary_reports_count_and_method():
    text = format_series_summary(12, "ImagePositionPatient")
    assert "12" in text
    assert "ImagePositionPatient" in text
