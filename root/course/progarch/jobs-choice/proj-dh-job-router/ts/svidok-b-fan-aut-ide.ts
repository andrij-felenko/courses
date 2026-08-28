function launchRollout(sys: ReturnType<typeof makeSystem>, id: string,
                       image: string, devices: string[], crash: boolean): void {
  try {
    withTransaction(sys.db, (tx) => {
      tx.insert("campaigns", { id, image, state: "launched" });               // корінець-кампанія
      sys.enqueue({ cls: "fleetRollout", key: `rollout:${id}`,
                    payload: { devices, image } }, tx);                       // → outbox у ТІЙ ЖЕ tx
      if (crash) throw new Error("збій до commit");
    });
  } catch { /* відкотилось */ }
}

const sys = makeSystem();
const count = (t: string) => sys.db.table(t).length;
const fleet = ["dev-1", "dev-2", "dev-3", "dev-4", "dev-5"];

launchRollout(sys, "camp-X", "fw-2.0", fleet, true);                         // невдала спроба
console.log("ВІДКАТ кампанії → campaigns:", count("campaigns"),
            " outbox:", count("outbox"), " брокер:", sys.broker.depth("fleetRollout"));

launchRollout(sys, "camp-Y", "fw-2.0", fleet, false);                        // успішний запуск
console.log("COMMIT кампанії → campaigns:", count("campaigns"),
            " брокер ДО relay:", sys.broker.depth("fleetRollout"));

const fanned = sys.outbox.relay();                                          // relay розсіює лавину
console.log("після relay    → фан-аут у брокер:", fanned,
            " брокер:", sys.broker.depth("fleetRollout"));
