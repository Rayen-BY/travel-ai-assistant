"""Schema and validation helpers for the travel-query dataset."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping


DATASET_FIELDS = ("id", "texte", "langue", "categorie", "sous_categorie")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TAXONOMY_PATH = PROJECT_ROOT / "config" / "dataset_taxonomy.json"


class DatasetValidationError(ValueError):
    """Raised when a dataset row or a complete dataset is invalid."""


def load_taxonomy(path: str | Path = DEFAULT_TAXONOMY_PATH) -> dict:
    """Load the category and language configuration from JSON."""

    with Path(path).open(encoding="utf-8") as config_file:
        return json.load(config_file)


def validate_row(row: Mapping[str, str], taxonomy: Mapping | None = None) -> None:
    """Validate one CSV row, raising ``DatasetValidationError`` on failure."""

    taxonomy = taxonomy or load_taxonomy()
    actual_fields = set(row)
    expected_fields = set(DATASET_FIELDS)
    if actual_fields != expected_fields:
        missing = sorted(expected_fields - actual_fields)
        extra = sorted(actual_fields - expected_fields)
        raise DatasetValidationError(
            f"Schéma invalide (champs manquants={missing}, champs inattendus={extra})."
        )

    empty_fields = [field for field in DATASET_FIELDS if not str(row[field]).strip()]
    if empty_fields:
        raise DatasetValidationError(f"Champs vides: {empty_fields}.")

    language = row["langue"]
    if language not in taxonomy["language_codes"]:
        raise DatasetValidationError(f"Code langue invalide: {language!r}.")

    category = row["categorie"]
    if category not in taxonomy["categories"]:
        raise DatasetValidationError(f"Catégorie invalide: {category!r}.")

    subcategory = row["sous_categorie"]
    if subcategory not in taxonomy["categories"][category]:
        raise DatasetValidationError(
            f"Sous-catégorie {subcategory!r} invalide pour {category!r}."
        )


def load_dataset(path: str | Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV dataset and preserve the declared schema."""

    with Path(path).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if tuple(reader.fieldnames or ()) != DATASET_FIELDS:
            raise DatasetValidationError(
                f"En-tête attendu: {','.join(DATASET_FIELDS)}."
            )
        return list(reader)


def validate_dataset(
    rows: Iterable[Mapping[str, str]],
    taxonomy: Mapping | None = None,
    *,
    require_complete_matrix: bool = False,
) -> None:
    """Validate rows, uniqueness and optionally the full taxonomy/language matrix."""

    taxonomy = taxonomy or load_taxonomy()
    materialized_rows = list(rows)
    for row in materialized_rows:
        validate_row(row, taxonomy)

    ids = [row["id"] for row in materialized_rows]
    if len(ids) != len(set(ids)):
        raise DatasetValidationError("Les identifiants doivent être uniques.")

    texts = [row["texte"] for row in materialized_rows]
    if len(texts) != len(set(texts)):
        raise DatasetValidationError("Le dataset contient un texte dupliqué exactement.")

    if require_complete_matrix:
        expected = {
            (category, subcategory, language)
            for category, subcategories in taxonomy["categories"].items()
            for subcategory in subcategories
            for language in taxonomy["language_codes"]
        }
        counts = Counter(
            (row["categorie"], row["sous_categorie"], row["langue"])
            for row in materialized_rows
        )
        missing = sorted(expected - set(counts))
        unexpected = sorted(set(counts) - expected)
        repeated = sorted(key for key, count in counts.items() if count != 1)
        if missing or unexpected or repeated:
            raise DatasetValidationError(
                "Matrice catégorie/sous-catégorie/langue invalide "
                f"(manquantes={missing}, inattendues={unexpected}, répétées={repeated})."
            )
