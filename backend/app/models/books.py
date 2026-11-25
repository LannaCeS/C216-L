from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        Index(
            "uq_books_normalized_title",
            text("lower(trim(title))"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    author: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    rating: Mapped[int | None] = mapped_column(nullable=True, default=None)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
