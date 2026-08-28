interface Page { items: DeviceDTO[]; nextCursor: string | null; }

class Hub {
  // Грубо, але ОБМЕЖЕНО: сторінка по limit; курсор — id, з якого починати далі.
  snapshotPage(cursor: string | null, limit: number): Page {
    const ids = this.ids();
    const start = cursor ? ids.indexOf(cursor) + 1 : 0;
    const items = ids.slice(start, start + limit).map(id => {
      const d = this.get(id);
      return { v: 1 as const, id: d.id, type: d.type(), room: d.room(),
               state: d.state(), brightness: d.brightness(), lastSeen: d.lastSeen() };
    });
    const last = items.length ? items[items.length - 1].id : null;
    return { items, nextCursor: start + limit < ids.length ? last : null };
  }
}

async function pullAll(hub: Hub, link: Link): Promise<DeviceDTO[]> {
  const all: DeviceDTO[] = [];
  let cursor: string | null = null;
  do {
    const page = await link.cross(() => hub.snapshotPage(cursor, 200));  // 1 перехід/сторінка
    all.push(...page.items);
    cursor = page.nextCursor;
  } while (cursor);
  return all;                             // 5000 пристроїв → 25 переходів, не 25000
}
