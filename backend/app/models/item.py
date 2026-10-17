from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Item(Base):
    __tablename__ = "alunos"
    __table_args__ = (
        Index(
            "uq_alunos_normalized_name",
            text("lower(trim(name))"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    grade: Mapped[float | None] = mapped_column(nullable=True, default=None)
