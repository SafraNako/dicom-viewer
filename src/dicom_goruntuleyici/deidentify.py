"""Checking for and removing commonly patient-identifying DICOM tags, based
on the DICOM standard's own Basic Application Level Confidentiality Profile
(PS3.15 Annex E) -- a curated, commonly-used subset of it, not the full
profile (which also covers private tags, UIDs, burned-in annotations, and
curve/overlay data this tool doesn't otherwise touch).
"""

from __future__ import annotations

import copy

import pydicom

IDENTIFYING_TAG_KEYWORDS: list[str] = [
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientBirthTime",
    "PatientSex",
    "PatientAge",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "ReferringPhysicianName",
    "ReferringPhysicianAddress",
    "ReferringPhysicianTelephoneNumbers",
    "PhysiciansOfRecord",
    "PerformingPhysicianName",
    "OperatorsName",
    "InstitutionName",
    "InstitutionAddress",
    "AccessionNumber",
    "StudyID",
    "RequestingPhysician",
]


def find_identifying_data(dataset: pydicom.Dataset) -> dict[str, str]:
    """Returns {keyword: value} for every identifying tag that is present
    AND non-empty in the dataset."""
    found = {}
    for keyword in IDENTIFYING_TAG_KEYWORDS:
        value = getattr(dataset, keyword, None)
        if value is not None and str(value).strip() != "":
            found[keyword] = str(value)
    return found


def deidentify(dataset: pydicom.Dataset) -> pydicom.Dataset:
    """Returns a deep-copied dataset with identifying tags removed. Never
    mutates the input dataset."""
    cleaned = copy.deepcopy(dataset)
    for keyword in IDENTIFYING_TAG_KEYWORDS:
        if hasattr(cleaned, keyword):
            delattr(cleaned, keyword)
    return cleaned
