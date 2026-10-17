from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.item import Item


class ItemRepository:
    """Database operations for items."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, grade: float | None = None) -> Item:
        item = Item(name=name, grade=grade)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_by_id(self, item_id: int) -> Item | None:
        return self.db.get(Item, item_id)

    def get_by_name(self, name: str) -> Item | None:
        normalized_name = name.strip().lower()
        return self.db.scalar(
            select(Item).where(func.lower(func.trim(Item.name)) == normalized_name)
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Item]:
        statement = select(Item).order_by(Item.id).offset(skip).limit(limit)
        return list(self.db.scalars(statement))

    def update(self, item: Item, changes: dict) -> Item:
        for field, value in changes.items():
            setattr(item, field, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Item) -> None:
        self.db.delete(item)
        self.db.commit()

    def delete_all(self) -> None:
        self.db.execute(delete(Item))
        self.db.commit()
