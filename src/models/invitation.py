from pydantic import BaseModel


class InvitationForm(BaseModel):
    type: str
    date: str
    time: str
    city: str
    address: str
    email: str


class InvitationResult(BaseModel):
    result: str
    invitation: str
    email: str
