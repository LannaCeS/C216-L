from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.item import Item
from app.repositories.item import ItemRepository


class GradeAlreadyExistsError(Exception):
    """Raised when a grade already exists for the supplied name."""


class GradeNotFoundError(Exception):
    """Raised when no grade exists for the supplied name."""


class GradeService:
    """Apply grade rules using the SQLAlchemy repository."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ItemRepository(db)

    def create_grade(self, name: str, grade: float) -> list[Item]:
        if self.repository.get_by_name(name):
            raise GradeAlreadyExistsError(name)
        try:
            self.repository.create(name, grade)
        except IntegrityError as error:
            self.db.rollback()
            raise GradeAlreadyExistsError(name) from error
        return self.repository.get_all()

    def list_grades(self) -> list[Item]:
        return self.repository.get_all()

    def get_grade(self, name: str) -> Item:
        item = self.repository.get_by_name(name)
        if item is None:
            raise GradeNotFoundError(name)
        return item

    def update_grade(self, name: str, new_grade: float) -> list[Item]:
        item = self.get_grade(name)
        self.repository.update(item, {"grade": new_grade})
        return self.repository.get_all()

    def replace_grade(self, name: str, new_grade: float) -> list[Item]:
        item = self.get_grade(name)
        try:
            self.repository.update(item, {"name": name, "grade": new_grade})
        except IntegrityError as error:
            self.db.rollback()
            raise GradeAlreadyExistsError(name) from error
        return self.repository.get_all()

    def delete_all_grades(self) -> None:
        self.repository.delete_all()
