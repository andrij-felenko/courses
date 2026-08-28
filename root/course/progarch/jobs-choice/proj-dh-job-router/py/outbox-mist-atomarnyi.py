# ── МІСТ для класу «викатка на флот»: корінець-кампанія + рядок outbox
# однією транзакцією (атомарно з базою), а relay уже РОЗСІЮЄ лавину в брокер. ──
class OutboxBridge:
    def __init__(self, db: Db, broker: Broker):
        self.db = db
        self.broker = broker

    def put(self, job: Job, tx: Tx | None = None) -> None:
        row = {"key": job.key, "cls": job.cls, "payload": job.payload, "sent": False}
        if tx is not None:
            tx.insert("outbox", row)          # у ту саму транзакцію, що й корінець
            return
        own = self.db.begin()
        own.insert("outbox", row)
        own.commit()

    def relay(self) -> int:
        # Окремий relay: читає ЗАКОМІЧЕНІ невислані рядки, розгортає фан-аут у брокер, мітить sent.
        pending = [r for r in self.db.table("outbox") if not r["sent"]]
        fanned = 0
        for r in pending:
            p = r["payload"]
            for dev in p["devices"]:          # один outbox-рядок → задача на КОЖЕН пристрій
                self.broker.put(Job("fleetRollout", {"device": dev, "image": p["image"]},
                                    f'{r["key"]}:{dev}'))
                fanned += 1
            r["sent"] = True                  # цей рядок розсіяно — вдруге не візьмемо
        return fanned
