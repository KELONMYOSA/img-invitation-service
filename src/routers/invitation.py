from fastapi import APIRouter, HTTPException, status

from src.models.invitation import InvitationForm, InvitationResult
from src.utils.img_gen import create_invitation
from src.utils.mail import send_email_with_attachment

router = APIRouter(
    prefix="/invitation",
    tags=["Image invitation generation"],
)


@router.post("", response_model=InvitationResult)
async def gen_img_and_send_email(data: InvitationForm):
    try:
        img = create_invitation(data)
        send_email_with_attachment(data, img)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))  # noqa: B904
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))  # noqa: B904
    return InvitationResult(result="Invitation created", invitation=data.type, email=data.email)
