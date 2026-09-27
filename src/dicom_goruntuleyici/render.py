"""Plain-text formatting for CLI output, kept separate from cli.py so it's
testable without going through argparse."""

from __future__ import annotations


def format_dataset_info(*, modality: str, rows: int, columns: int, rescale_slope: float, rescale_intercept: float, default_window, pixel_spacing) -> str:
    lines = ["=== DICOM DOSYA BİLGİSİ ==="]
    lines.append(f"Modalite: {modality}")
    lines.append(f"Boyut: {rows} x {columns} piksel")
    lines.append(f"RescaleSlope / RescaleIntercept: {rescale_slope} / {rescale_intercept}")
    if pixel_spacing is not None:
        lines.append(f"Piksel aralığı (mm): {pixel_spacing}")
    if default_window is not None:
        wc, ww = default_window
        lines.append(f"Dosyanın önerdiği pencere: WC={wc}, WW={ww}")
    else:
        lines.append("Dosyada önerilen pencere (WindowCenter/Width) yok")
    return "\n".join(lines)


def format_identifying_tags(tags: dict[str, str], *, show_values: bool) -> str:
    lines = ["=== KİMLİK BELİRLEYİCİ ETİKET KONTROLÜ ==="]
    if not tags:
        lines.append("Kimlik belirleyici etiket bulunamadı.")
        return "\n".join(lines)
    lines.append(f"{len(tags)} kimlik belirleyici etiket bulundu:")
    for keyword, value in tags.items():
        if show_values:
            lines.append(f"  {keyword}: {value}")
        else:
            lines.append(f"  {keyword}: [gizli -- göstermek için --degerleri-goster]")
    return "\n".join(lines)


def format_deidentify_result(*, removed_count: int, output_path: str) -> str:
    lines = ["=== ANONİMLEŞTİRME ==="]
    lines.append(f"{removed_count} etiket kaldırıldı.")
    lines.append(f"Anonimleştirilmiş kopya yazıldı: {output_path}")
    return "\n".join(lines)


def format_series_summary(n_slices: int, sort_method: str) -> str:
    lines = ["=== SERİ ==="]
    lines.append(f"Dilim sayısı: {n_slices}")
    lines.append(f"Sıralama yöntemi: {sort_method}")
    return "\n".join(lines)
