# all_transitions_test.py — пробігає ВСІ 4×4 пари й доводить те саме, що TS-версія.
STATES = [Status.NEW, Status.ONLINE, Status.OFFLINE, Status.RETIRED]

def device_in(s):                                # привести у стан лише законним шляхом
    d = Device("dut")
    if s is not Status.NEW:                     d.commission("home-1")
    if s in (Status.OFFLINE, Status.RETIRED):   d.mark_offline()
    if s is Status.RETIRED:                     d.retire()
    return d

INVOKE = {
    "commission":  lambda d: d.commission("home-9"),
    "markOffline": lambda d: d.mark_offline(),
    "markOnline":  lambda d: d.mark_online(),
    "retire":      lambda d: d.retire(),
}

def test_all_transitions():
    for s in STATES:
        for c in COMMANDS:
            legal = TRANSITIONS.get((s, c))       # очікуваний перехід або None
            noop = IDEMPOTENT.get(c) == s         # ідемпотентний повтор?
            d = device_in(s); d.pull_events()     # відкинути події налаштування
            if legal is not None:
                INVOKE[c](d)
                assert d.state is legal, f"{s.value}×{c}: мав перейти в {legal.value}"
                assert len(d.pull_events()) == 1, f"{s.value}×{c}: рівно одна подія"
            elif noop:
                INVOKE[c](d)
                assert d.state is s, f"{s.value}×{c}: no-op не міняє стан"
                assert d.pull_events() == [], f"{s.value}×{c}: no-op без події"
            else:
                try:
                    INVOKE[c](d); assert False, f"{s.value}×{c}: мав кинути"
                except DomainError:
                    pass
                assert d.state is s, f"{s.value}×{c}: стан незмінний після кидка"
                assert d.pull_events() == [], f"{s.value}×{c}: збій без події"

def test_golden_intent():                         # намір дому — НЕЗАЛЕЖНО від таблиці
    try: Device("x").retire(); assert False
    except DomainError: pass                      # невведений не списують
    r = device_in(Status.RETIRED)
    try: r.mark_online(); assert False
    except DomainError: pass                      # мертвий не оживе
    o = device_in(Status.ONLINE); o.pull_events()
    o.mark_online()
    assert o.pull_events() == []                  # повтор online — no-op, без Reconnected

if __name__ == "__main__":
    test_all_transitions(); test_golden_intent()
    print(f"покрито {len(STATES) * len(COMMANDS)} пар (стан × команда) ✓")
