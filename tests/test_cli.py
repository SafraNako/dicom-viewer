from __future__ import annotations

import shutil
import subprocess
import sys

from dicom_goruntuleyici.cli import main


def test_bilgi_smoke(capsys, ct_small_path):
    exit_code = main(["bilgi", "--dosya", ct_small_path])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "DICOM DOSYA BİLGİSİ" in out
    assert "CT" in out


def test_bilgi_hides_identifying_values_by_default(capsys, ct_small_path):
    exit_code = main(["bilgi", "--dosya", ct_small_path])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "CompressedSamples" not in out
    assert "gizli" in out


def test_bilgi_shows_identifying_values_with_flag(capsys, ct_small_path):
    exit_code = main(["bilgi", "--dosya", ct_small_path, "--degerleri-goster"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "CompressedSamples" in out


def test_goruntule_with_preset(tmp_path, ct_small_path):
    png = tmp_path / "out.png"
    exit_code = main(["goruntule", "--dosya", ct_small_path, "--pencere", "kemik", "--grafik", str(png)])
    assert exit_code == 0
    assert png.exists() and png.stat().st_size > 0


def test_goruntule_with_custom_wc_ww(tmp_path, ct_small_path):
    png = tmp_path / "out.png"
    exit_code = main(["goruntule", "--dosya", ct_small_path, "--wc", "50", "--ww", "350", "--grafik", str(png)])
    assert exit_code == 0
    assert png.exists()


def test_goruntule_without_window_or_default_fails_gracefully(capsys, ct_small_path):
    exit_code = main(["goruntule", "--dosya", ct_small_path])
    out = capsys.readouterr().out
    assert exit_code == 1
    assert "Hata" in out


def test_pencere_karsilastir_smoke(capsys, tmp_path, ct_small_path):
    png = tmp_path / "cmp.png"
    exit_code = main(["pencere-karsilastir", "--dosya", ct_small_path, "--grafik", str(png)])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "akciger" in out
    assert png.exists()


def test_seri_smoke(capsys, tmp_path, ct_small_path, mr_small_path):
    shutil.copy(ct_small_path, tmp_path / "a.dcm")
    shutil.copy(mr_small_path, tmp_path / "b.dcm")
    exit_code = main(["seri", "--dizin", str(tmp_path)])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Dilim sayısı: 2" in out


def test_seri_with_montage(tmp_path, ct_small_path, mr_small_path):
    shutil.copy(ct_small_path, tmp_path / "a.dcm")
    shutil.copy(mr_small_path, tmp_path / "b.dcm")
    png = tmp_path / "montage.png"
    exit_code = main(["seri", "--dizin", str(tmp_path), "--grafik", str(png)])
    assert exit_code == 0
    assert png.exists()


def test_seri_with_single_slice_index(tmp_path, ct_small_path):
    shutil.copy(ct_small_path, tmp_path / "a.dcm")
    png = tmp_path / "slice0.png"
    exit_code = main(["seri", "--dizin", str(tmp_path), "--dilim-indeksi", "0", "--grafik", str(png)])
    assert exit_code == 0
    assert png.exists()


def test_seri_empty_directory_fails_gracefully(capsys, tmp_path):
    exit_code = main(["seri", "--dizin", str(tmp_path)])
    out = capsys.readouterr().out
    assert exit_code == 1
    assert "Hata" in out


def test_anonimlestir_writes_clean_copy(tmp_path, ct_small_path):
    output = tmp_path / "clean.dcm"
    exit_code = main(["anonimlestir", "--dosya", ct_small_path, "--cikti", str(output)])
    assert exit_code == 0
    assert output.exists()

    import pydicom
    cleaned = pydicom.dcmread(str(output))
    assert not hasattr(cleaned, "PatientName") or str(cleaned.PatientName) == ""


def test_missing_subcommand_exits_nonzero():
    result = subprocess.run(
        [sys.executable, "-m", "dicom_goruntuleyici.cli"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0


def test_installed_console_script_end_to_end(ct_small_path):
    result = subprocess.run(
        ["dicom-goruntuleyici", "bilgi", "--dosya", ct_small_path],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0
    assert "DICOM DOSYA BİLGİSİ" in result.stdout
