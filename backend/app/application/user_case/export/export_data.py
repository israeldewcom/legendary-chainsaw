from dataclasses import dataclass
import uuid
import pandas as pd
import io
from datetime import datetime
from typing import List, Optional
from app.domain.repositories.transaction import TransactionRepository
from app.domain.repositories.receipt import ReceiptRepository
from app.application.interfaces.storage import Storage
from app.application.interfaces.background_job import BackgroundJobService
from app.application.dtos import ExportRequestDTO
from app.common.exceptions import BusinessError
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class ExportDataUseCase:
    transaction_repo: TransactionRepository
    receipt_repo: ReceiptRepository
    storage: Storage
    job_service: BackgroundJobService

    async def request(self, user_id: int, dto: ExportRequestDTO) -> str:
        export_id = str(uuid.uuid4())
        # Create background job
        await self.job_service.create_job(
            job_type="data_export",
            params={
                "export_id": export_id,
                "user_id": user_id,
                "dto": dto.__dict__,
            }
        )
        return export_id

    async def generate(self, export_id: str, user_id: int, dto: ExportRequestDTO) -> str:
        # Fetch transactions
        filters = {}
        if dto.date_from:
            filters["date__gte"] = dto.date_from
        if dto.date_to:
            filters["date__lte"] = dto.date_to
        if dto.client_ids:
            filters["client_id__in"] = dto.client_ids
        if dto.categories:
            filters["category__in"] = dto.categories

        transactions = await self.transaction_repo.get_by_user_id(user_id, limit=10000, filters=filters)

        # Convert to DataFrame
        data = []
        for tx in transactions:
            data.append({
                "Date": tx.date.isoformat(),
                "Description": tx.description,
                "Amount": float(tx.amount.amount),
                "Currency": tx.currency,
                "Category": tx.category.value if tx.category else "",
                "Subcategory": tx.subcategory or "",
                "Vendor": tx.vendor or "",
                "Client ID": tx.client_id,
                "Status": tx.status,
                "Tags": ",".join(tx.tags),
            })

        df = pd.DataFrame(data)

        # Generate file in requested format
        if dto.format == "csv":
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            content = buffer.getvalue().encode("utf-8")
            content_type = "text/csv"
            extension = "csv"
        elif dto.format == "excel":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Transactions")
            content = buffer.getvalue()
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            extension = "xlsx"
        else:
            raise BusinessError(f"Unsupported format: {dto.format}")

        # Upload to S3
        key = f"exports/user_{user_id}/{export_id}.{extension}"
        await self.storage.upload(
            bucket=settings.AWS_S3_EXPORT_BUCKET,
            key=key,
            data=io.BytesIO(content) if isinstance(content, bytes) else io.BytesIO(content),
            content_type=content_type,
        )

        # Generate signed URL
        url = await self.storage.generate_presigned_url(
            bucket=settings.AWS_S3_EXPORT_BUCKET,
            key=key,
            expires_in=604800,  # 7 days
        )

        logger.info("Export generated", export_id=export_id, user_id=user_id, format=dto.format)
        return url
