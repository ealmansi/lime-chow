import re
from datetime import datetime

class EventUtils:
    separator = "-"

    def build_id(venue, date, title):
        id = EventUtils.separator.join([venue, date, title]).lower()
        id = id.replace("ausverkauft", "")
        id = re.sub("[^a-z0-9]+", EventUtils.separator, id)
        id = id[:80]
        id = id.strip(EventUtils.separator)
        return id

    def get_current_datetime():
        return datetime.now().isoformat()
