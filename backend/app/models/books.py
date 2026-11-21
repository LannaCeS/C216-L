from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        Index(
            "uq_books_normalized_title",
            text("lower(trim(title)))"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    rate: Mapped[float | None] = mapped_column(nullable=True, default=None)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)