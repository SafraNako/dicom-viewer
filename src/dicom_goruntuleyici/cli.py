from __future__ import annotations

import argparse
import sys

from .deidentify import deidentify, find_identifying_data
from .export import save_comparison_grid, save_image, save_montage
from .loader import get_default_window, get_pixel_array, get_rescale_params, load_dataset, load_series
from .render import format_dataset_info, format_deidentify_result, format_identifying_tags, format_series_summary
from .series import sort_method_used, sort_series
from .windowing import STANDARD_PRESETS, apply_modality_and_voi_lut


def _cmd_bilgi(args: argparse.Namespace) -> int:
    ds = load_dataset(args.dosya)
    slope, intercept = get_rescale_params(ds)
    pixel_spacing = getattr(ds, "PixelSpacing", None)
    print(format_dataset_info(
        modality=str(getattr(ds, "Modality", "?")), rows=int(ds.Rows), columns=int(ds.Columns),
        rescale_slope=slope, rescale_intercept=intercept, default_window=get_default_window(ds),
        pixel_spacing=list(pixel_spacing) if pixel_spacing is not None else None,
    ))
    print()
    tags = find_identifying_data(ds)
    print(format_identifying_tags(tags, show_values=args.degerleri_goster))
    return 0


def _cmd_goruntule(args: argparse.Namespace) -> int:
    ds = load_dataset(args.dosya)
    arr = get_pixel_array(ds)
    slope, intercept = get_rescale_params(ds)

    if args.pencere:
        wc, ww = STANDARD_PRESETS[args.pencere]
    elif args.wc is not None and args.ww is not None:
        wc, ww = args.wc, args.ww
    else:
        default = get_default_window(ds)
        if default is None:
            print("Hata: --pencere, --wc/--ww verilmedi ve dosyada varsayılan pencere yok.")
            return 1
        wc, ww = default

    windowed = apply_modality_and_voi_lut(arr, slope, intercept, wc, ww)
    print(f"Uygulanan pencere: WC={wc}, WW={ww}")
    print(f"Sonuç aralığı: [{windowed.min():.1f}, {windowed.max():.1f}]")

    if args.grafik:
        save_image(args.grafik, windowed, title=f"WC={wc}, WW={ww}")
        print(f"Grafik yazıldı: {args.grafik}")
    return 0


def _cmd_pencere_karsilastir(args: argparse.Namespace) -> int:
    ds = load_dataset(args.dosya)
    arr = get_pixel_array(ds)
    slope, intercept = get_rescale_params(ds)

    images = {}
    for name, (wc, ww) in STANDARD_PRESETS.items():
        images[f"{name} (WC={wc}, WW={ww})"] = apply_modality_and_voi_lut(arr, slope, intercept, wc, ww)

    print(f"{len(images)} standart pencere ön ayarı uygulandı: {', '.join(STANDARD_PRESETS)}")
    if args.grafik:
        save_comparison_grid(args.grafik, images, suptitle="Standart pencere ön ayarları karşılaştırması")
        print(f"Grafik yazıldı: {args.grafik}")
    return 0


def _cmd_seri(args: argparse.Namespace) -> int:
    datasets = load_series(args.dizin)
    if not datasets:
        print("Hata: dizinde okunabilir DICOM dosyası bulunamadı.")
        return 1
    method = sort_method_used(datasets)
    ordered = sort_series(datasets)
    print(format_series_summary(len(ordered), method))

    if args.dilim_indeksi is not None:
        if not (0 <= args.dilim_indeksi < len(ordered)):
            print(f"Hata: --dilim-indeksi [0, {len(ordered)-1}] aralığında olmalı.")
            return 1
        ds = ordered[args.dilim_indeksi]
        arr = get_pixel_array(ds)
        slope, intercept = get_rescale_params(ds)
        wc, ww = STANDARD_PRESETS[args.pencere] if args.pencere else (get_default_window(ds) or STANDARD_PRESETS["yumusak_doku"])
        windowed = apply_modality_and_voi_lut(arr, slope, intercept, wc, ww)
        if args.grafik:
            save_image(args.grafik, windowed, title=f"Dilim {args.dilim_indeksi}, WC={wc}, WW={ww}")
            print(f"Grafik yazıldı: {args.grafik}")
    elif args.grafik:
        wc, ww = STANDARD_PRESETS[args.pencere] if args.pencere else STANDARD_PRESETS["yumusak_doku"]
        rendered = []
        for ds in ordered:
            arr = get_pixel_array(ds)
            slope, intercept = get_rescale_params(ds)
            rendered.append(apply_modality_and_voi_lut(arr, slope, intercept, wc, ww))
        save_montage(args.grafik, rendered, suptitle=f"Seri ({method} ile sıralı), WC={wc}, WW={ww}")
        print(f"Grafik yazıldı: {args.grafik}")
    return 0


def _cmd_anonimlestir(args: argparse.Namespace) -> int:
    ds = load_dataset(args.dosya)
    tags = find_identifying_data(ds)
    print(format_identifying_tags(tags, show_values=args.degerleri_goster))

    if args.cikti:
        cleaned = deidentify(ds)
        cleaned.save_as(args.cikti)
        print()
        print(format_deidentify_result(removed_count=len(tags), output_path=args.cikti))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dicom-goruntuleyici",
        description="DICOM görüntüleyici (alt komutlar: bilgi, goruntule, pencere-karsilastir, seri, anonimlestir).",
    )
    sub = parser.add_subparsers(dest="komut", required=True)

    p_bilgi = sub.add_parser("bilgi", help="DICOM dosyasının meta verilerini ve kimlik belirleyici etiket durumunu göster")
    p_bilgi.add_argument("--dosya", required=True, help="DICOM dosya yolu")
    p_bilgi.add_argument("--degerleri-goster", action="store_true", help="Kimlik belirleyici etiket değerlerini de yazdır (varsayılan: yalnızca hangi etiketlerin bulunduğu)")
    p_bilgi.set_defaults(func=_cmd_bilgi)

    p_view = sub.add_parser("goruntule", help="Pencereleme (windowing) uygulayıp görüntüyü PNG olarak kaydet")
    p_view.add_argument("--dosya", required=True, help="DICOM dosya yolu")
    p_view.add_argument("--pencere", choices=list(STANDARD_PRESETS), default=None, help="Standart pencere ön ayarı")
    p_view.add_argument("--wc", type=float, default=None, help="Özel pencere merkezi (Window Center)")
    p_view.add_argument("--ww", type=float, default=None, help="Özel pencere genişliği (Window Width)")
    p_view.add_argument("--grafik", metavar="DOSYA", help="Bu PNG dosyasına görüntüyü çiz")
    p_view.set_defaults(func=_cmd_goruntule)

    p_cmp = sub.add_parser("pencere-karsilastir", help="Tüm standart pencere ön ayarlarını aynı görüntüye uygulayıp karşılaştır")
    p_cmp.add_argument("--dosya", required=True, help="DICOM dosya yolu")
    p_cmp.add_argument("--grafik", metavar="DOSYA", help="Bu PNG dosyasına karşılaştırma ızgarası çiz")
    p_cmp.set_defaults(func=_cmd_pencere_karsilastir)

    p_series = sub.add_parser("seri", help="Bir dizindeki DICOM serisini sırala ve görselleştir")
    p_series.add_argument("--dizin", required=True, help="DICOM dosyalarını içeren dizin")
    p_series.add_argument("--dilim-indeksi", type=int, default=None, help="Yalnızca bu indeksteki dilimi çiz (verilmezse tüm seri bir montaj olarak çizilir)")
    p_series.add_argument("--pencere", choices=list(STANDARD_PRESETS), default=None, help="Standart pencere ön ayarı (varsayılan: yumusak_doku)")
    p_series.add_argument("--grafik", metavar="DOSYA", help="Bu PNG dosyasına çiz")
    p_series.set_defaults(func=_cmd_seri)

    p_anon = sub.add_parser("anonimlestir", help="Kimlik belirleyici etiketleri kontrol et ve isteğe bağlı olarak temizlenmiş bir kopya yaz")
    p_anon.add_argument("--dosya", required=True, help="DICOM dosya yolu")
    p_anon.add_argument("--degerleri-goster", action="store_true", help="Kimlik belirleyici etiket değerlerini de yazdır")
    p_anon.add_argument("--cikti", metavar="DOSYA", help="Anonimleştirilmiş kopyanın yazılacağı dosya yolu")
    p_anon.set_defaults(func=_cmd_anonimlestir)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
