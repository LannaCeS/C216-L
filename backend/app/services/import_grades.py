"""One-time importer for legacy grades stored in data/grades.json."""

import json
import math
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from app.database.session import SessionLocal
from app.models.item import Item
from app.repositories.item import ItemRepository

GRADE_FILE = Path(__file__).resolve().parents[2] / "data" / "grades.json"


def import_grades() -> tuple[int, int]:
    if not GRADE_FILE.exists():
        raise FileNotFoundError(f"Legacy grade file not found: {GRADE_FILE}")

    rows = json.loads(GRADE_FILE.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("The legacy grade file must contain a JSON array.")

    inserted = skipped = 0
    seen_names: set[str] = set()
    with SessionLocal() as db:
        repository = ItemRepository(db)
        try:
            for row in rows:
                if not isinstance(row, dict) or "name" not in row or "grade" not in row:
                    raise ValueError("Each row must contain 'name' and 'grade'.")
                name = str(row["name"]).strip()
                try:
                    grade = float(row["grade"])
                except (TypeError, ValueError) as error:
                    raise ValueError(f"Invalid numeric grade for {name!r}.") from error
                if not name or len(name) > 100 or not math.isfinite(grade):
                    raise ValueError(f"Invalid name or numeric grade for {name!r}.")

                normalized_name = name.strip().lower()
                if normalized_name in seen_names or repository.get_by_name(name):
                    skipped += 1
                    continue
                seen_names.add(normalized_name)
                db.add(Item(name=name, grade=grade))
                inserted += 1

            db.commit()
        except (ValueError, IntegrityError):
            db.rollback()
            raise

    return inserted, skipped


if __name__ == "__main__":
    added, existing = import_grades()
    print(f"Imported {added} grade(s); skipped {existing} existing record(s).")
