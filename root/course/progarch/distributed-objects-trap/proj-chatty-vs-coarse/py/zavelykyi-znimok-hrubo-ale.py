@dataclass
class Page:
    items: list
    next_cursor: "str | None"

class Hub:
    # Грубо, але ОБМЕЖЕНО: сторінка по limit; курсор — id, з якого починати далі.
    def snapshot_page(self, cursor, limit):
        ids = self.ids()
        start = ids.index(cursor) + 1 if cursor else 0
        window = ids[start:start + limit]
        items = [DeviceDTO(1, d.id, d.type(), d.room(), d.state(),
                           d.brightness(), d.last_seen())
                 for d in (self.get(i) for i in window)]
        nxt = window[-1] if start + limit < len(ids) else None
        return Page(items, nxt)

async def pull_all(hub, link):
    out, cursor = [], None
    while True:
        page = await link.cross(lambda: hub.snapshot_page(cursor, 200))  # 1 перехід/сторінка
        out += page.items
        cursor = page.next_cursor
        if cursor is None:
            break
    return out                            # 5000 пристроїв → 25 переходів, не 25000
