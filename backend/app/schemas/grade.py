from pydantic import BaseModel


class GradeSettings(BaseModel):
    name: str
    grade: str
