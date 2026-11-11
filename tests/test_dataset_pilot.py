"""Automated quality checks for the 75-row pilot dataset."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

import pytest

from travel_ai_assistant.dataset.schema import (
    DATASET_FIELDS,
    DatasetValidationError,
    load_dataset,
    load_taxonomy,
    validate_dataset,
    validate_row,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "pilot" / "travel_queries_pilot.csv"

EXPECTED_LANGUAGES = ["FR", "EN", "AR", "TN_AR", "TN_LAT"]
EXPECTED_CATEGORIES = {
    "Vols": ["Recherche de vols", "Prix", "Horaires"],
    "Hébergement": ["Recherche d'hôtels", "Prix", "Disponibilité"],
    "Météo": ["Météo actuelle", "Prévisions", "Climat saisonnier"],
    "Change": ["Taux de change", "Conversion de devises", "Monnaie locale"],
    "Destinations": [
        "Informations touristiques",
        "Activités",
        "Conseils de voyage",
    ],
}


@pytest.fixture(scope="module")
def taxonomy() -> dict:
    return load_taxonomy()


@pytest.fixture(scope="module")
def rows() -> list[dict[str, str]]:
    return load_dataset(DATASET_PATH)


def test_taxonomy_is_exact(taxonomy: dict) -> None:
    assert taxonomy == {
        "language_codes": EXPECTED_LANGUAGES,
        "categories": EXPECTED_CATEGORIES,
    }
    assert sum(map(len, taxonomy["categories"].values())) == 15


def test_csv_schema_is_exact(rows: list[dict[str, str]]) -> None:
    assert rows
    assert tuple(rows[0]) == DATASET_FIELDS


def test_csv_has_no_blank_physical_line() -> None:
    lines = DATASET_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 76  # One header plus 75 data rows.
    assert all(line.strip() for line in lines)


def test_pilot_contains_exactly_75_valid_non_empty_rows(
    rows: list[dict[str, str]], taxonomy: dict
) -> None:
    assert len(rows) == 75
    for row in rows:
        validate_row(row, taxonomy)
        assert all(value.strip() for value in row.values())


def test_ids_and_texts_have_no_exact_duplicates(rows: list[dict[str, str]]) -> None:
    assert len({row["id"] for row in rows}) == len(rows)
    assert len({row["texte"] for row in rows}) == len(rows)


def test_every_subcategory_language_combination_appears_once(
    rows: list[dict[str, str]], taxonomy: dict
) -> None:
    validate_dataset(rows, taxonomy, require_complete_matrix=True)
    counts = Counter(
        (row["categorie"], row["sous_categorie"], row["langue"])
        for row in rows
    )
    assert len(counts) == 75
    assert set(counts.values()) == {1}


def test_language_distribution_is_balanced(rows: list[dict[str, str]]) -> None:
    assert Counter(row["langue"] for row in rows) == Counter(
        {language: 15 for language in EXPECTED_LANGUAGES}
    )


def test_category_distribution_is_balanced(rows: list[dict[str, str]]) -> None:
    assert Counter(row["categorie"] for row in rows) == Counter(
        {category: 15 for category in EXPECTED_CATEGORIES}
    )


def test_tunisian_variants_use_the_expected_alphabet(
    rows: list[dict[str, str]],
) -> None:
    arabic_characters = re.compile(r"[\u0600-\u06ff]")
    tn_ar_texts = [row["texte"] for row in rows if row["langue"] == "TN_AR"]
    tn_lat_texts = [row["texte"] for row in rows if row["langue"] == "TN_LAT"]
    assert all(arabic_characters.search(text) for text in tn_ar_texts)
    assert all(not arabic_characters.search(text) for text in tn_lat_texts)


def test_validator_rejects_an_invalid_category(
    rows: list[dict[str, str]], taxonomy: dict
) -> None:
    invalid_row = dict(rows[0], categorie="Restauration")
    with pytest.raises(DatasetValidationError):
        validate_row(invalid_row, taxonomy)
