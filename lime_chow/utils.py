import re


class EventUtils:
    def build_event_id(venue, starts_on, title):
        sep = "-"
        id = sep.join([venue, starts_on, title]).lower()
        id = id.replace("ausverkauft", "")
        id = re.sub("[^a-z0-9]+", sep, id)
        id = id[:80]
        id = id.strip(sep)
        return id
