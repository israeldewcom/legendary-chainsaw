from openai import AsyncOpenAI
from typing import Tuple, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings
import structlog

logger = structlog.get_logger()


class OpenAICategorizer:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value() if settings.OPENAI_API_KEY else None)
        self.model = settings.OPENAI_MODEL
        self.fallback_model = settings.OPENAI_FALLBACK_MODEL

    @retry(stop=stop_after_attempt(settings.OPENAI_MAX_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def categorize(self, description: str, amount: float, vendor: Optional[str] = None, client_industry: Optional[str] = None) -> Tuple[str, Optional[str], float]:
        prompt = f"""Categorize the following transaction into one of the tax categories: advertising, auto, bank_fees, charitable, commissions, computer, continuing_education, contract_labor, dues_subscriptions, insurance, interest, legal_professional, meals, office, rent_lease, repairs_maintenance, supplies, taxes_licenses, travel, utilities, wages, other.

Transaction: {description}
Amount: {amount}
Vendor: {vendor or 'Unknown'}
Client Industry: {client_industry or 'Unknown'}

Return a JSON with fields: category, subcategory (if any, else null), confidence (0-1)."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            import json
            data = json.loads(content)
            category = data.get("category", "other")
            subcategory = data.get("subcategory")
            confidence = float(data.get("confidence", 0.5))
            return category, subcategory, confidence
        except Exception as e:
            logger.exception("OpenAI categorization failed", error=e)
            # Fallback to simple rule-based
            return self._rule_based_fallback(description, amount)

    def _rule_based_fallback(self, description: str, amount: float) -> Tuple[str, Optional[str], float]:
        desc_lower = description.lower()
        if "uber" in desc_lower or "lyft" in desc_lower or "taxi" in desc_lower:
            return "auto", None, 0.6
        if "starbucks" in desc_lower or "restaurant" in desc_lower or "cafe" in desc_lower:
            return "meals", None, 0.6
        if "amazon" in desc_lower or "walmart" in desc_lower or "store" in desc_lower:
            return "supplies", None, 0.5
        return "other", None, 0.3
