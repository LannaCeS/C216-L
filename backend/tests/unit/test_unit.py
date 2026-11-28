import pytest
from pydantic import ValidationError

from app.schemas.book import BookRating, BookRatingPatch
from app.services.auth import credentials_match


# login auth
def test_matching_credentials():
    assert credentials_match("a@b.com", "123", "a@b.com", "123")


def test_wrong_password():
    assert not credentials_match("a@b.com", "x", "a@b.com", "123")


def test_wrong_email():
    assert not credentials_match("x@b.com", "123", "a@b.com", "123")


def test_comparison_is_case_sensitive():
    assert not credentials_match("A@b.com", "123", "a@b.com", "123")


# schemas
def test_valid_book_is_accepted():
    book = BookRating(title="Dom Casmurro", author="Machado", rating=5, notes="ótimo")
    assert book.title == "Dom Casmurro"
    assert book.rating == 5


def test_title_is_required():
    with pytest.raises(ValidationError):
        BookRating(author="Machado", rating=5)


def test_empty_title_is_rejected():
    with pytest.raises(ValidationError):
        BookRating(title="", rating=5)


@pytest.mark.parametrize("rating", [-1, 6, 100])
def test_rating_out_of_range_is_rejected(rating):
    with pytest.raises(ValidationError):
        BookRating(title="Dom Casmurro", rating=rating)


@pytest.mark.parametrize("rating", [0, 1, 5])
def test_rating_in_range_is_accepted(rating):
    assert BookRating(title="Dom Casmurro", rating=rating).rating == rating


def test_patch_accepts_partial_payload():
    patch = BookRatingPatch(rating=4)
    assert patch.model_dump(exclude_unset=True) == {"rating": 4}
