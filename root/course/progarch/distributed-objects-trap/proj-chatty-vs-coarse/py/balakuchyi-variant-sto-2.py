def render(*_fields):                       # малює один рядок дашборда (заглушка)
    pass

# НА ХМАРІ — проксі. Виглядає як Device, але КОЖЕН геттер перетинає межу.
class RemoteDevice:
    def __init__(self, id, hub, link):
        self.id, self.hub, self.link = id, hub, link
    async def type(self):       return await self.link.cross(lambda: self.hub.get(self.id).type())
    async def room(self):       return await self.link.cross(lambda: self.hub.get(self.id).room())
    async def state(self):      return await self.link.cross(lambda: self.hub.get(self.id).state())
    async def brightness(self): return await self.link.cross(lambda: self.hub.get(self.id).brightness())
    async def last_seen(self):  return await self.link.cross(lambda: self.hub.get(self.id).last_seen())

async def render_chatty(ids, hub, link):
    for id in ids:                          # 30 пристроїв
        d = RemoteDevice(id, hub, link)
        render(await d.type(), await d.room(), await d.state(),
               await d.brightness(), await d.last_seen())   # 5 переходів на пристрій
