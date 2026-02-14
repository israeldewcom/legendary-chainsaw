from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Receipt:
    id: Optional[int] = None
    user_id: int = 0
    client_id: Optional[int] = None
    filename: Optional[str] = None
    s3_key: Optional[str] = None
    ocr_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, processing, processed, failed
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    page_count: Optional[int] = None
    processed_at: Optional[datetime] = None
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    transaction_id: Optional[int] = None

    def mark_processing(self) -> None:
        self.status = "processing"

    def mark_processed(self, ocr_text: str, extracted_data: Dict[str, Any]) -> None:
        self.status = "processed"
        self.ocr_text = ocr_text
        self.extracted_data = extracted_data
        self.processed_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        self.status = "failed"
        self.error_message = error

    def link_transaction(self, transaction_id: int) -> None:
        self.transaction_id = transaction_id
