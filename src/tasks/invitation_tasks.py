import logging

from src.celery_app import celery_app
from src.models.invitation import InvitationForm
from src.utils.img_gen import create_invitation
from src.utils.mail import send_email_with_attachment

logger = logging.getLogger(__name__)


@celery_app.task(name="generate_invitation_task")
def generate_invitation_task(invitation_data: dict):
    try:
        form = InvitationForm(**invitation_data)
        img_bytes = create_invitation(form)
        send_email_with_attachment(form, img_bytes)
        logger.info(f"Invitation created and sent successfully for {form.email}")
    except Exception as e:
        logger.error("Failed to create invitation for %s: %s",
                    invitation_data.get("email", "unknown"), str(e))
