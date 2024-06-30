from pydantic import BaseModel, Field


class InvitationForm(BaseModel):
    type: str
    date: str
    time: str
    address: str
    email: str


class InvitationResult(BaseModel):
    result: str
    invitation: str
    email: str


class TestModel(BaseModel):
    test: str = Field(..., pattern=r"^test$")
