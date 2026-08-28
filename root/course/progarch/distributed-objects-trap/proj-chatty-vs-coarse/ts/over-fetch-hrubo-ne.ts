// Грубо — не означає «усе підряд». Список малює лише кімнату й стан.
interface ListItemDTO { v: 1; id: string; room: string; state: string; }

class Hub {
  // ... snapshot() лишається для екрана деталей ...
  listView(): ListItemDTO[] {              // той самий 1 перехід, утричі менший пакунок
    return [...this.devices.values()].map(d =>
      ({ v: 1 as const, id: d.id, room: d.room(), state: d.state() }));
  }
}
