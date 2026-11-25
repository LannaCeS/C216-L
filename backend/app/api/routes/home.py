from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.models.books import Book
from app.schemas.book import BookRating, BookRatingPatch, BookRatingResponse

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[BookRatingResponse])
def list_rated_books(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.id).all()


@router.get("/{book_id}", response_model=BookRatingResponse)
def get_rated_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookRatingResponse, status_code=status.HTTP_201_CREATED)
def create_rated_book(payload: BookRating, db: Session = Depends(get_db)):
    new_book = Book(**payload.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.patch("/{book_id}", response_model=BookRatingResponse)
def update_rated_book(
    book_id: int,
    payload: BookRatingPatch,
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book

@router.put("/{book_id}", response_model=BookRatingResponse)
def replace_rated_book(
    book_id: int,
    payload: BookRating,
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    for field in payload.model_fields_set:
        setattr(book, field, getattr(payload, field))

    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rated_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
