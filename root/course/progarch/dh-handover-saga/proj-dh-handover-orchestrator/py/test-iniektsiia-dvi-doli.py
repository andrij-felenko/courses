import copy, pytest

def make_world(faults, claim_accepted=True):
    log, fired, seen, box = [], {}, set(), {"alerted": None}

    def act(name):
        async def _a(_ctx):                               # рахує й падає перші faults[name] разів
            fired[name] = fired.get(name, 0) + 1
            if fired[name] <= faults.get(name, 0):
                log.append(name + "✗"); raise RuntimeError("збій " + name)
            log.append(name)
        return _a

    async def wait_or_park(_ctx):
        log.append("post_invite")
        if not claim_accepted:
            raise WaitingForHuman(0)                       # паркуємось; 0 → одразу «протерміновано»
        log.append("accepted")

    S = [
        Step("freeze",        Kind.COMPENSATABLE, act("freeze"),        act("unfreeze")),
        Step("revoke_access", Kind.COMPENSATABLE, act("revoke_keys"),   act("restore_keys")),
        Step("await_claim",   Kind.COMPENSATABLE, wait_or_park,         act("cancel_claim")),
        Step("transfer_wipe", Kind.PIVOT,         act("transfer_shred")),
        Step("rebind",        Kind.RETRIABLE,     act("reissue_certs")),
        Step("billing",       Kind.RETRIABLE,     act("switch_billing")),
        Step("welcome",       Kind.RETRIABLE,     act("notify")),
    ]

    db = {}
    class Tx: ...
    class C:
        async def __aenter__(self): return Tx()
        async def __aexit__(self, *a): return False
    class P(Ports):
        async def load(self, i): return copy.deepcopy(db[i])
        async def persist(self, s): db[s.id] = copy.deepcopy(s)
        def txn(self): return C()                          # у пам'яті атомарна тривіально
        async def seen(self, _t, k): return k in seen
        async def mark(self, _t, k): seen.add(k)
        async def save_in(self, _t, s): db[s.id] = copy.deepcopy(s)
        async def outbox(self, _t, ev): pass
        async def alert(self, s, *a): box["alerted"] = s.id
    db["h1"] = Saga(id="h1", home_id="home-1")
    return S, P(), log, fired, box

COMPS = ["cancel_claim", "restore_keys", "unfreeze"]

@pytest.mark.asyncio
async def test_before_pivot_clean_abort():
    S, p, log, fired, box = make_world({}, claim_accepted=False)
    saga = await drive(p, "h1", S)                         # дійде до await_claim і запаркується
    assert saga.status == "waiting"
    await on_claim_deadline(p, "h1", S)                    # витримка вичерпана
    saga = await p.load("h1")
    assert saga.status == "aborted"                                       # чисте скасування
    assert [x for x in log if x in COMPS] == COMPS                        # рівно зворотний порядок
    assert "transfer_shred" not in fired                                  # ПІВОТ не настав

@pytest.mark.asyncio
async def test_after_pivot_transient_retries():
    S, p, log, fired, box = make_world({"switch_billing": 2})
    saga = await drive(p, "h1", S)
    assert saga.status == "done"
    assert fired["switch_billing"] == 3                    # 2 падіння + 1 успіх
    assert fired["transfer_shred"] == 1                    # півот стався
    assert not any(x in COMPS for x in log)                # нічого не відкочено

@pytest.mark.asyncio
async def test_after_pivot_stuck_to_dlq():
    S, p, log, fired, box = make_world({"switch_billing": 999})
    saga = await drive(p, "h1", S)
    assert saga.status == "stuck"                          # застрягло → мертва черга
    assert box["alerted"] == "h1"                          # людину покликано
    assert fired["switch_billing"] == MAX_ATTEMPTS + 1
    assert fired["transfer_shred"] == 1                    # передане лишається переданим
    assert not any(x in COMPS for x in log)                # нічого не відкочено

@pytest.mark.asyncio
async def test_crash_at_terminal_resolves_done():
    S, p, log, fired, box = make_world({})
    # Щілина: остання транзакція вже посунула cursor за останній крок,
    # але persist(status="done") не встиг — крах саме тут.
    await p.persist(Saga(id="h1", home_id="home-1", cursor=len(S)))
    saga = await drive(p, "h1", S)
    assert saga.status == "done"      # підйом дочитав термінал із курсора
    assert box["alerted"] is None     # у DLQ не здавали — сага завершилась
    assert log == []                  # жодного кроку не перезапущено
