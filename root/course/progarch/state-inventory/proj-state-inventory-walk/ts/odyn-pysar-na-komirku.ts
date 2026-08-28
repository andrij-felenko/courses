class StatusView {
  private byId = new Map<number, any>();

  refresh(d: Device): void {                    // ЄДИНИЙ шлях запису — завжди з пристрою
    this.byId.set(d.id, { temp: d.temp, online: d.online, ts: Date.now() });
  }

  get(deviceId: number) {                       // усі інші лише читають
    const row = this.byId.get(deviceId);
    if (row && Date.now() - row.ts > TIMEOUT_S * 1000)
      return { ...row, stale: true };           // свіжість позначена, а не прихована
    return row;
  }
}
