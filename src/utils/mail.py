import json
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import settings
from src.models.invitation import InvitationForm


def _load_config(config_path: str) -> dict:
    try:
        with open(config_path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as e:
        raise FileNotFoundError("Config file not found: " + str(e))  # noqa: B904


def _load_email_template(template_path: str) -> str:
    try:
        with open(template_path, encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as e:
        raise FileNotFoundError("Email template not found: " + str(e))  # noqa: B904


def send_email_with_attachment(invitation_data: InvitationForm, attachment: bytes):
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = invitation_data.email
    msg["Subject"] = "Приглашение на мероприятие от QuestGuru"

    config = _load_config(settings.CONFIG_PATH)
    phone = config["city2phone"].get(invitation_data.city)
    mail = config["city2email"].get(invitation_data.city)
    vk = config["city2vk"].get(invitation_data.city)

    html_template = _load_email_template("storage/email/template.html")
    html_content = html_template.format(
        date=invitation_data.date,
        time=invitation_data.time,
        address=invitation_data.address,
        phone=phone,
        vk=vk,
        mail=mail,
    )
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment; filename=QuestGuru.jpg")
    msg.attach(part)

    try:
        with open("storage/email/assets/logo.png", "rb") as logo:
            img = MIMEImage(logo.read())
            img.add_header("Content-ID", "<logo>")
            img.add_header("Content-Disposition", "inline", filename="logo.png")
            msg.attach(img)
    except FileNotFoundError as e:
        raise FileNotFoundError("Email logo not found: " + str(e))  # noqa: B904

    with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, invitation_data.email, msg.as_string())
