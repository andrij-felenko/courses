def launch_rollout(sys, campaign_id: str, image: str, devices: list[str], crash: bool) -> None:
    try:
        with transaction(sys.db) as tx:
            tx.insert("campaigns", {"id": campaign_id, "image": image, "state": "launched"})  # корінець
            sys.enqueue(Job("fleetRollout", {"devices": devices, "image": image},
                            f"rollout:{campaign_id}"), tx)                    # → outbox у ТІЙ ЖЕ tx
            if crash:
                raise RuntimeError("збій до commit")
    except RuntimeError:
        pass  # відкотилось


sys = make_system()
count = lambda t: len(sys.db.table(t))
fleet = ["dev-1", "dev-2", "dev-3", "dev-4", "dev-5"]

launch_rollout(sys, "camp-X", "fw-2.0", fleet, True)                         # невдала спроба
print("ВІДКАТ кампанії → campaigns:", count("campaigns"),
      " outbox:", count("outbox"), " брокер:", sys.broker.depth("fleetRollout"))

launch_rollout(sys, "camp-Y", "fw-2.0", fleet, False)                        # успішний запуск
print("COMMIT кампанії → campaigns:", count("campaigns"),
      " брокер ДО relay:", sys.broker.depth("fleetRollout"))

fanned = sys.outbox.relay()                                                 # relay розсіює лавину
print("після relay    → фан-аут у брокер:", fanned,
      " брокер:", sys.broker.depth("fleetRollout"))
