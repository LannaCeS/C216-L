from app.models.books import Book

class BookRepository:
    def __init__(self, db):
        self.db = db
        
    def create(self, book):
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def get_all(self):
        return self.db.query(Book).all()