from pydantic import BaseModel, Field


class BookRating(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(default="")
    notes: str = Field(default="")
    rating: int = Field(..., ge=0, le=5)


class BookRatingPatch(BaseModel):
    title: str = Field(default=None, min_length=1)
    author: str | None = Field(default=None)
    notes: str | None = Field(default=None)
    rating: int | None = Field(default=None, ge=0, le=5)


class BookRatingResponse(BaseModel):
    id: int
    title: str
    author: str | None
    notes: str | None
    rating: int | None

    model_config = {"from_attributes": True}
