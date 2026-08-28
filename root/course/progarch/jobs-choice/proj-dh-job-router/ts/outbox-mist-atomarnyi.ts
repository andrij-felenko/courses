// ── МІСТ для класу «викатка на флот»: корінець-кампанія + рядок outbox
// однією транзакцією (атомарно з базою), а relay уже РОЗСІЮЄ лавину в брокер. ──
class OutboxBridge implements Substrate {
  constructor(private db: Db, private broker: Broker) {}
  put(job: Job, tx?: Tx): void {
    const row = { key: job.key, cls: job.cls, payload: job.payload, sent: false };
    if (tx) { tx.insert("outbox", row); return; }    // у ту саму транзакцію, що й корінець
    const own = this.db.begin(); own.insert("outbox", row); own.commit();
  }
  // Окремий relay: читає ЗАКОМІЧЕНІ невислані рядки, розгортає фан-аут у брокер, мітить sent.
  relay(): number {
    const pending = this.db.table("outbox").filter(r => r.sent === false);
    let fanned = 0;
    for (const r of pending) {
      const p = r.payload as { devices: string[]; image: string };
      for (const dev of p.devices) {                 // один outbox-рядок → задача на КОЖЕН пристрій
        this.broker.put({ cls: "fleetRollout", key: `${r.key}:${dev}`,
                          payload: { device: dev, image: p.image } });
        fanned++;
      }
      r.sent = true;                                  // цей рядок розсіяно — вдруге не візьмемо
    }
    return fanned;
  }
}
