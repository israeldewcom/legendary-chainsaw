from dataclasses import dataclass
import uuid
import json
import zipfile
import io
from datetime import datetime
from app.domain.repositories.user import UserRepository
from app.domain.repositories.client import ClientRepository
from app.domain.repositories.transaction import TransactionRepository
from app.domain.repositories.receipt import ReceiptRepository
from app.application.interfaces.storage import Storage
from app.application.interfaces.email_sender import EmailSender
from app.application.interfaces.background_job import BackgroundJobService
from app.common.exceptions import NotFoundError
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class ExportPersonalDataUseCase:
    user_repo: UserRepository
    client_repo: ClientRepository
    transaction_repo: TransactionRepository
    receipt_repo: ReceiptRepository
    storage: Storage
    email_sender: EmailSender
    job_service: BackgroundJobService

    async def request(self, user_id: int) -> str:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        user.request_data_export()
        await self.user_repo.save(user)

        export_id = str(uuid.uuid4())
        await self.job_service.create_job(
            job_type="gdpr_export",
            params={"export_id": export_id, "user_id": user_id}
        )
        return export_id

    async def generate(self, export_id: str, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return

        # Collect all user data
        clients = await self.client_repo.get_by_user_id(user_id, limit=10000)
        transactions = []
        receipts = []
        for client in clients:
            tx_list = await self.transaction_repo.get_by_client_id(client.id, limit=10000)
            transactions.extend(tx_list)
            rc_list = await self.receipt_repo.get_by_client_id(client.id, limit=10000)
            receipts.extend(rc_list)

        # Build JSON
        export_data = {
            "user": {
                "email": user.email.value,
                "full_name": user.full_name,
                "company_name": user.company_name,
                "created_at": user.created_at.isoformat(),
                "preferences": user.preferences,
                "subscription_tier": user.subscription_tier,
                "subscription_status": user.subscription_status,
                "affiliate_earnings": float(user.affiliate_earnings.amount),
                "affiliate_balance": float(user.affiliate_balance.amount),
            },
            "clients": [
                {
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "phone": c.phone,
                    "address": c.address,
                    "tax_year": c.tax_year,
                    "filing_status": c.filing_status,
                    "ein": c.ein,
                    "industry": c.industry,
                    "notes": c.notes,
                    "created_at": c.created_at.isoformat(),
                }
                for c in clients
            ],
            "transactions": [
                {
                    "id": t.id,
                    "client_id": t.client_id,
                    "date": t.date.isoformat(),
                    "description": t.description,
                    "amount": float(t.amount.amount),
                    "currency": t.currency,
                    "category": t.category.value if t.category else None,
                    "subcategory": t.subcategory,
                    "status": t.status,
                    "reviewed": t.reviewed,
                    "vendor": t.vendor,
                    "receipt_id": t.receipt_id,
                    "tags": t.tags,
                    "created_at": t.created_at.isoformat(),
                }
                for t in transactions
            ],
            "receipts": [
                {
                    "id": r.id,
                    "filename": r.filename,
                    "s3_key": r.s3_key,
                    "status": r.status,
                    "uploaded_at": r.uploaded_at.isoformat(),
                    "processed_at": r.processed_at.isoformat() if r.processed_at else None,
                }
                for r in receipts
            ],
        }

        # Create zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("user_data.json", json.dumps(export_data, indent=2, default=str))
            # Include receipt images
            for receipt in receipts:
                if receipt.s3_key:
                    # Download from S3
                    file_data = await self.storage.download(settings.AWS_S3_BUCKET, receipt.s3_key)
                    if file_data:
                        zf.writestr(f"receipts/{receipt.filename or receipt.s3_key}", file_data)

        zip_buffer.seek(0)
        key = f"gdpr-exports/user_{user_id}/{export_id}.zip"
        await self.storage.upload(
            bucket=settings.AWS_S3_EXPORT_BUCKET,
            key=key,
            data=zip_buffer,
            content_type="application/zip"
        )

        # Generate signed URL
        url = await self.storage.generate_presigned_url(
            bucket=settings.AWS_S3_EXPORT_BUCKET,
            key=key,
            expires_in=604800  # 7 days
        )

        # Update user
        user.data_exported_at = datetime.utcnow()
        user.data_export_key = key
        await self.user_repo.save(user)

        # Send email
        await self.email_sender.send_email(
            to=[user.email.value],
            subject="Your TaxFlow AI data export is ready",
            template_name="data_export_ready.html",
            template_context={"download_url": url, "expires_in": "7 days"}
        )

        logger.info("GDPR export completed", user_id=user_id, key=key)
