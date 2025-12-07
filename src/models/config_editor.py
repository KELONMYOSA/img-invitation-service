from typing import Literal

from pydantic import BaseModel, Field, field_validator


class City(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    email: str = Field(min_length=1)
    vk: str = Field(min_length=1)


class TextItem(BaseModel):
    type: Literal["date", "time", "address"]
    x: int
    y: int
    font: str
    size: int = Field(ge=1)
    color: str

    @field_validator("color")
    @classmethod
    def color_must_be_hex(cls, v: str) -> str:
        value = v.strip()
        if not value.startswith("#") or len(value) not in (4, 7):
            raise ValueError("color must be HEX like #FFF or #RRGGBB")
        return value


class Preset(BaseModel):
    name: str = Field(min_length=1)
    template: str = Field(min_length=1)
    texts: list[TextItem]

    @field_validator("texts")
    @classmethod
    def must_have_unique_types(cls, v: list[TextItem]) -> list[TextItem]:
        seen: set[str] = set()
        for item in v:
            if item.type in seen:
                raise ValueError("texts must contain unique types (date, time, address)")
            seen.add(item.type)
        required = {"date", "time", "address"}
        if set(seen) != required:
            missing = required - set(seen)
            raise ValueError(f"missing text types: {', '.join(sorted(missing))}")
        return v
