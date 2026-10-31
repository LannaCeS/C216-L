from pydantic import BaseModel, ConfigDict, Field


class GradeSettings(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    grade: float = Field(allow_inf_nan=False)
