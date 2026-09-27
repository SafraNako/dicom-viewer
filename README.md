# dicom-viewer

A DICOM medical image viewer: windowing/leveling implemented exactly per
the DICOM standard's own formula (not an approximation), series navigation,
and a de-identification tag checker/stripper. CLI and internal package
names are in Turkish (`dicom-goruntuleyici` / `dicom_goruntuleyici`),
consistent with the other tools in this project series; code and this
document are in English.

> **Not a diagnostic tool.** This displays pixel data and metadata; it does
> not interpret, diagnose, or offer any clinical judgment, and (like the
> rest of this roadmap category) is not approved for clinical use.

## Why pydicom instead of parsing DICOM from scratch

Several earlier projects in this series parse binary formats from scratch
as a deliberate learning exercise (ISO 9660, PE/COFF headers, SSH packet
framing, DNS wire format). DICOM is a different scale of problem: the
standard runs to over 20 parts and thousands of pages, with dozens of
transfer syntaxes and compression schemes (JPEG, JPEG2000, RLE...). Writing
a correct, general DICOM parser from scratch would be reinventing a
large, well-tested wheel badly. [pydicom](https://pydicom.github.io/) is
the established, actively-maintained open-source library for this -- using
it is the same judgment call as using `torchvision` in #25 (image
classifier) or `EasyOCR` in #29 (OCR system) rather than a from-scratch
model. What *is* built from scratch here, and is the part actually
responsible for correctness, is the image-processing pipeline: the
Modality LUT + VOI LUT windowing math.

## What's actually being validated

- **[`windowing.py`](src/dicom_goruntuleyici/windowing.py)** -- the exact
  pseudo-code from DICOM PS3.3 Section C.11.2.1.2.1 (the "LINEAR" VOI LUT
  function), fetched directly from the standard itself rather than trusted
  from memory. Hand-verified test cases use round numbers
  (window center=100, width=101) chosen so every threshold and the
  formula's output can be computed by hand and checked exactly -- including
  a genuinely non-obvious detail the standard itself defines: a value
  exactly at the window center does **not** map to exactly the midpoint of
  the output range for finite window widths (it's off by `0.5/(width-1)`
  of the range) -- confirmed against real sample data, documented in the
  code, and deliberately not "fixed" away, since doing so would make the
  implementation diverge from the standard.
- **[`series.py`](src/dicom_goruntuleyici/series.py)** -- slices are sorted
  by `ImagePositionPatient` projected onto the series' actual slice-normal
  direction (computed from `ImageOrientationPatient`), not just raw
  z-coordinate, with a fallback to `InstanceNumber` and then original file
  order. Verified with synthetic multi-slice datasets fed in deliberately
  scrambled order.
- **[`deidentify.py`](src/dicom_goruntuleyici/deidentify.py)** -- a curated
  subset of DICOM's own Basic Application Level Confidentiality Profile
  (PS3.15 Annex E) identifying tags. Verified to find and remove real
  identifying fields in a real (sample) dataset, and to never mutate the
  original dataset.

## Test data: pydicom's own bundled samples, not live TCIA downloads

The roadmap note for this item suggested testing against public archives
like [TCIA](https://www.cancerimagingarchive.net/). This tool instead uses
**pydicom's own bundled sample DICOM files** (`CT_small.dcm`, `MR_small.dcm`,
shipped inside the `pydicom` package itself, e.g.
`CompressedSamples^CT1` / patient ID `1CT1` -- obviously synthetic/sample
identifiers, not real patient data) for all 55 tests. This was a deliberate
choice over live TCIA downloads: it's genuinely public, already-anonymized
data (distributed specifically for testing DICOM tooling), but doesn't
require network access at test time -- which matters for CI reliability
(no flaky downloads, no rate limits) and means this repository never
fetches or stores any external medical dataset at all.

## Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

dicom-goruntuleyici bilgi --dosya scan.dcm
dicom-goruntuleyici goruntule --dosya scan.dcm --pencere kemik --grafik kemik.png
dicom-goruntuleyici pencere-karsilastir --dosya scan.dcm --grafik karsilastirma.png
dicom-goruntuleyici seri --dizin ./seri_klasoru --grafik montaj.png
dicom-goruntuleyici anonimlestir --dosya scan.dcm --cikti temiz.dcm
```

`bilgi` and `anonimlestir` hide identifying tag *values* by default
(printing only which tags were found) -- pass `--degerleri-goster` to show
them. This is deliberately the default, not an afterthought: the tool
might be pointed at a real file, not just the bundled samples.

### Standard window presets

`--pencere` accepts `akciger` (lung), `kemik` (bone), `beyin` (brain), and
`yumusak_doku` (soft tissue) -- widely-cited radiology conventions (Window
Center / Window Width in Hounsfield Units): lung -600/1500, bone 400/1800,
brain 40/80, soft tissue 50/350. These are, as every source describing them
notes, typical/approximate conventions, not a fixed part of the DICOM
standard -- `--wc`/`--ww` accept any custom values.

## Testing

```bash
pytest -v
```

55 tests, no mocking -- every assertion is a hand-verified formula value,
a real (sample) DICOM file check, or a synthetic dataset with fully
controlled, known values. Pure numerical/I/O Python, no Linux/Docker
dependency (same as the rest of this roadmap category).

## Scope and limitations

- **Not a diagnostic tool** and not approved for clinical use.
- The de-identification tag list is a curated *subset* of DICOM's Basic
  Confidentiality Profile (PS3.15 Annex E) -- common patient/institution/
  physician identifying fields. It does not cover the full profile (private
  tags, UIDs, burned-in pixel annotations, curve/overlay data, structured
  report content).
- 2D slice-by-slice viewing only -- no 3D volume rendering or
  multi-planar reconstruction (MPR).
- Compression/transfer-syntax support is whatever pydicom (and its
  optional pixel-data-handler plugins) provides; this tool doesn't add
  anything on top of that.

## License

MIT -- see [LICENSE](LICENSE).
