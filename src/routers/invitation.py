from fastapi import APIRouter

router = APIRouter(
    prefix="/invitation",
    tags=["Image invitation generation"],
)


@router.post("")
async def gen_img_and_send_email():
    return {"result": "success"}
