import io
import json
import os

from PIL import Image, ImageDraw, ImageFont

from src.config import settings
from src.models.invitation import InvitationForm


def _load_config(config_path: str) -> dict:
    try:
        with open(config_path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError("Config file not found: " + str(e))  # noqa: B904


def _draw_text_on_image(image: Image, text: str, position: tuple[int, int], font_path: str, font_size: int, color: str):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=color)


def _gen_invitation_img(template: str, texts_config: list, invitation_data: InvitationForm) -> bytes:
    if not os.path.exists(template):
        raise FileNotFoundError("Template image not found: " + template)

    image = Image.open(template)
    type2text = {"date": invitation_data.date, "time": invitation_data.time, "address": invitation_data.address}
    for text_item in texts_config:
        font_path = os.path.join(settings.FONT_FOLDER, text_item["font"])
        if not os.path.exists(font_path):
            raise FileNotFoundError("Font not found: " + str(font_path))
        _draw_text_on_image(
            image,
            type2text[text_item["type"]],
            (int(text_item["x"]), int(text_item["y"])),
            str(font_path),
            text_item["size"],
            text_item["color"],
        )

    with io.BytesIO() as buf:
        image.save(buf, format="JPEG")
        img_bytes = buf.getvalue()

    return img_bytes


def create_invitation(invitation_data: InvitationForm) -> bytes:
    config = _load_config(settings.CONFIG_PATH)["presets"]
    for preset in config:
        if preset["name"] == invitation_data.type:
            texts_config = preset["texts"]
            template_path = os.path.join(settings.TEMPLATE_FOLDER, preset["template"])
            return _gen_invitation_img(str(template_path), texts_config, invitation_data)
    raise ValueError("Preset not found")
