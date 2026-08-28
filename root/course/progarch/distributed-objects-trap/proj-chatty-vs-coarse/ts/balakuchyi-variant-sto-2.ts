function render(..._fields: unknown[]) {}   // малює один рядок дашборда (заглушка)

// НА ХМАРІ — проксі. Виглядає як Device, але КОЖЕН геттер перетинає межу.
class RemoteDevice {
  constructor(private id: string, private hub: Hub, private link: Link) {}
  type()       { return this.link.cross(() => this.hub.get(this.id).type()); }
  room()       { return this.link.cross(() => this.hub.get(this.id).room()); }
  state()      { return this.link.cross(() => this.hub.get(this.id).state()); }
  brightness() { return this.link.cross(() => this.hub.get(this.id).brightness()); }
  lastSeen()   { return this.link.cross(() => this.hub.get(this.id).lastSeen()); }
}

async function renderChatty(ids: string[], hub: Hub, link: Link) {
  for (const id of ids) {                   // 30 пристроїв
    const d = new RemoteDevice(id, hub, link);
    render(await d.type(), await d.room(), await d.state(),
           await d.brightness(), await d.lastSeen());   // 5 переходів на пристрій
  }
}
