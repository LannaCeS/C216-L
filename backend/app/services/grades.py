import json
from pathlib import Path

GRADE_FILE = Path(__file__).resolve().parents[2] / "data" / "grades.json"


class GradeAlreadyExistsError(Exception):
    """Raised when a grade already exists for the supplied name."""


class GradeNotFoundError(Exception):
    """Raised when no grade exists for the supplied name."""


def _read_grades() -> list[dict[str, str]]:
    if not GRADE_FILE.exists():
        return []
    contents = GRADE_FILE.read_text(encoding="utf-8").strip()
    if not contents:
        return []
    return json.loads(contents)


def _write_grades(grades: list[dict[str, str]]) -> None:
    GRADE_FILE.parent.mkdir(parents=True, exist_ok=True)
    GRADE_FILE.write_text(json.dumps(grades, indent=2), encoding="utf-8")


def _same_name(saved_name: str, requested_name: str) -> bool:
    return saved_name.strip().casefold() == requested_name.strip().casefold()


def create_grade(name: str, grade: str) -> list[dict[str, str]]:
    grades = _read_grades()
    if any(_same_name(item["name"], name) for item in grades):
        raise GradeAlreadyExistsError(name)

    grades.append({"name": name, "grade": grade})
    _write_grades(grades)
    return grades


def list_grades() -> list[dict[str, str]]:
    return _read_grades()


def get_grade(name: str) -> dict[str, str]:
    for grade in _read_grades():
        if _same_name(grade["name"], name):
            return grade
    raise GradeNotFoundError(name)


def update_grade(name: str, new_grade: str) -> list[dict[str, str]]:
    grades = _read_grades()
    for saved_grade in grades:
        if _same_name(saved_grade["name"], name):
            saved_grade["grade"] = new_grade
            _write_grades(grades)
            return grades
    raise GradeNotFoundError(name)


def replace_grade(name: str, new_grade: str) -> list[dict[str, str]]:
    grades = _read_grades()
    for index, saved_grade in enumerate(grades):
        if _same_name(saved_grade["name"], name):
            grades[index] = {"name": name, "grade": new_grade}
            _write_grades(grades)
            return grades
    raise GradeNotFoundError(name)


def delete_all_grades() -> None:
    if GRADE_FILE.exists():
        GRADE_FILE.unlink()
