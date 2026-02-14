from mixpanel import Mixpanel
from app.config import settings
import structlog

logger = structlog.get_logger()


class MixpanelClient:
    def __init__(self):
        if settings.MIXPANEL_TOKEN:
            self.mp = Mixpanel(settings.MIXPANEL_TOKEN)
        else:
            self.mp = None

    def track(self, user_id: int, event_name: str, properties: dict = None):
        if not self.mp:
            return
        try:
            self.mp.track(str(user_id), event_name, properties)
            logger.debug("Analytics tracked", user_id=user_id, event=event_name)
        except Exception as e:
            logger.exception("Analytics tracking failed", error=e)

    def people_set(self, user_id: int, properties: dict):
        if not self.mp:
            return
        try:
            self.mp.people_set(str(user_id), properties)
        except Exception as e:
            logger.exception("Analytics people_set failed", error=e)
