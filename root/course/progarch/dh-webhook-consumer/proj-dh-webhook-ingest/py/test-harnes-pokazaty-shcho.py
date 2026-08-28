import pytest, json, time, hmac, hashlib, os

sent: list = []
set_notifier(lambda ev: sent.append(ev))          # шпигун замість справжнього пуша

def sign(body: dict):                              # підписуємо, як це робив би провайдер
    raw = json.dumps(body).encode()
    t = int(time.time())
    v1 = hmac.new(os.environ["ACME_WEBHOOK_SECRET"].encode(),
                  f"{t}.".encode() + raw, hashlib.sha256).hexdigest()
    return raw, f"t={t},v1={v1}"

async def drain(pool):
    while await process_once(pool):
        pass

@pytest.mark.asyncio
async def test_duplicate_processed_once(pool):
    await reset_db(pool); sent.clear()
    raw, header = sign({"id": "e1", "device_id": "lock-42", "state": "open", "seq": 5})
    assert await handle_webhook(raw, header, pool) == 200
    assert await handle_webhook(raw, header, pool) == 200   # провайдер повторив
    assert await count_rows(pool, "jobs") == 1              # у чергу лягло ОДИН раз
    await drain(pool)
    assert (await get_twin(pool, "lock-42"))["state"] == "open"
    assert len(sent) == 1                                   # один пуш, не два

@pytest.mark.asyncio
async def test_reorder_older_does_not_win(pool):
    await reset_db(pool); sent.clear()
    a = sign({"id": "e2", "device_id": "lock-42", "state": "open",   "seq": 5})
    b = sign({"id": "e3", "device_id": "lock-42", "state": "closed", "seq": 4})  # старіша!
    await handle_webhook(*a, pool); await handle_webhook(*b, pool)
    await drain(pool)
    twin = await get_twin(pool, "lock-42")
    assert twin["state"] == "open" and twin["seq"] == 5     # seq 4 не перебив seq 5

@pytest.mark.asyncio
async def test_lost_event_caught_by_reconcile(pool):
    await reset_db(pool); sent.clear()
    await seed_twin(pool, "lock-42", "closed", 5)          # остання відома правда
    async def partner(_id): return {"state": "open", "seq": 6}   # подія seq=6 НЕ дійшла
    await reconcile_device(pool, "lock-42", partner)
    assert (await get_twin(pool, "lock-42"))["state"] == "open"  # звірка стягла до джерела
    assert sent[-1]["state"] == "open"                     # і сповістила про виправлення

@pytest.mark.asyncio
async def test_poison_goes_to_dead_letter(pool):
    await reset_db(pool); sent.clear()
    bad  = sign({"id": "e4", "device_id": "lock-42", "state": "???",  "seq": 7})  # впаде щоразу
    good = sign({"id": "e5", "device_id": "lock-9",  "state": "open", "seq": 1})
    await handle_webhook(*bad, pool); await handle_webhook(*good, pool)
    for _ in range(MAX_ATTEMPTS):                          # без чекання на backoff
        await force_ready(pool); await drain(pool)
    assert await count_rows(pool, "dead_letter") == 1      # отруйна осіла в DLQ
    assert (await get_twin(pool, "lock-9"))["state"] == "open"  # здорова пройшла
    assert await count_rows(pool, "jobs") == 0             # черга чиста
