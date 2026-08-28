# НА ХМАРІ пакунок знову стає об'єктом — зі СВОЄЮ поведінкою (локальною, даровою).
class CloudDevice:
    def __init__(self, id, type, room, state, brightness, last_seen):
        self.id, self.type, self.room = id, type, room
        self.state, self.brightness, self.last_seen = state, brightness, last_seen

    @classmethod
    def from_dto(cls, dto):
        return cls(dto.id, dto.type, dto.room, dto.state, dto.brightness, dto.last_seen)

    def is_stale(self, now): return now - self.last_seen > 60
    def label(self):         return f"{self.room}: {self.type}"

async def render_coarse(hub, link, now):
    dtos = await link.cross(hub.snapshot)          # 1 перехід — увесь знімок
    devices = [CloudDevice.from_dto(x) for x in dtos]
    for d in devices:
        render(d.label(), d.state, d.brightness, d.is_stale(now))   # локально, дарма
