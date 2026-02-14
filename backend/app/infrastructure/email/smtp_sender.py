from typing import List, Dict, Any
import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.config import settings
import structlog

logger = structlog.get_logger()


class SMTPEmailSender:
    def __init__(self):
        self.template_env = Environment(
            loader=FileSystemLoader(settings.EMAIL_TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_email(self, to: List[str], subject: str, template_name: str, template_context: Dict[str, Any]) -> None:
        # Render template
        template = self.template_env.get_template(template_name)
        html_body = template.render(**template_context)

        # Build email
        msg = EmailMessage()
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = ", ".join(to)
        msg["Subject"] = subject
        msg.set_content(html_body, subtype="html")

        # Send via SMTP
        try:
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD.get_secret_value() if settings.SMTP_PASSWORD else None,
                use_tls=settings.SMTP_PORT == 587,  # STARTTLS
            )
            logger.info("Email sent", to=to, subject=subject, template=template_name)
        except Exception as e:
            logger.exception("Failed to send email", to=to, subject=subject, error=e)
            raise
