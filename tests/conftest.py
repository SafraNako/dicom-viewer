from __future__ import annotations

import numpy as np
import pydicom
import pytest
from pydicom.dataset import Dataset, FileMetaDataset


@pytest.fixture
def ct_small_path() -> str:
    from pydicom.data import get_testdata_file

    return get_testdata_file("CT_small.dcm")


@pytest.fixture
def mr_small_path() -> str:
    from pydicom.data import get_testdata_file

    return get_testdata_file("MR_small.dcm")


def make_synthetic_ct_slice(z_position: float, instance_number: int, fill_value: int = 100) -> Dataset:
    """A minimal, valid, entirely synthetic CT-like dataset -- no real
    patient data anywhere, used to test sorting/windowing logic with fully
    controlled, known values."""
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = Dataset()
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.SOPClassUID = pydicom.uid.CTImageStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.Modality = "CT"
    ds.Rows, ds.Columns = 4, 4
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.ImagePositionPatient = [0.0, 0.0, z_position]
    ds.ImageOrientationPatient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    ds.InstanceNumber = instance_number
    ds.RescaleSlope = 1.0
    ds.RescaleIntercept = -1024.0
    ds.PixelData = (np.ones((4, 4), dtype=np.uint16) * fill_value).tobytes()
    return ds
