from fastapi import APIRouter, Depends, Form, HTTPException, status

from src.models.invitation import InvitationForm, InvitationResult
from src.utils.auth import verify_api_key
from src.utils.img_gen import create_invitation
from src.utils.mail import send_email_with_attachment

router = APIRouter(
    prefix="/invitation",
    tags=["Image invitation generation"],
)


@router.post("", response_model=InvitationResult | dict, dependencies=[Depends(verify_api_key)])
async def gen_img_and_send_email(
    type: str | None = Form(None),
    date: str | None = Form(None),
    time: str | None = Form(None),
    address: str | None = Form(None),
    email: str | None = Form(None),
    test: str | None = Form(None),
):
    if test == "test":
        return {"test": "Success"}
    elif all((type, date, time, address, email)):
        try:
            data = InvitationForm(type=type, date=date, time=time, address=address, email=email)
            img = create_invitation(data)
            send_email_with_attachment(data, img)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))  # noqa: B904
        except FileNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))  # noqa: B904
        return InvitationResult(result="Invitation created", invitation=data.type, email=data.email)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data format")
