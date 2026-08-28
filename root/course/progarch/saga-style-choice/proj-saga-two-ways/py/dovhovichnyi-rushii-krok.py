class Step:
    def __init__(self, name, run, comp): self.name, self.run, self.comp = name, run, comp

class Store:                                  # «диск» — переживає смерть процесу саги
    def __init__(self): self.db = {}
    def load(self, sid):        return self.db.get(sid)
    def save(self, sid, state): self.db[sid] = dict(state)   # копія = «лягло на диск»

class ProcessKilled(Exception):               # імітація жорсткої смерті процесу
    pass

async def run_saga(sid, steps, store):
    st = store.load(sid) or {"cursor": 0, "status": "running"}

    # ── ВІДРОДЖЕННЯ: диск каже не лише «доки дійшло» (cursor), а й «куди йшло» (status) ──
    if st["status"] in ("committed", "compensated"):
        return                                          # уже завершено
    if st["status"] == "compensating":
        await _roll_back(sid, steps, store, st); return # помер ПОСЕРЕД відкоту → дороби відкіт, не прямий хід

    try:
        while st["cursor"] < len(steps):
            await steps[st["cursor"]].run()
            st["cursor"] += 1
            store.save(sid, st)               # ← крок зафіксовано на диску ПЕРЕД наступним
        st["status"] = "committed"; store.save(sid, st)
    except ProcessKilled:                     # не відкіт — процес помер, диск лишився
        store.save(sid, st); raise
    except Exception:                         # бізнес-збій → компенсуємо зворотним порядком
        st["status"] = "compensating"; store.save(sid, st)   # ← спершу зафіксуй НАПРЯМОК на диску, тоді відкочуй
        await _roll_back(sid, steps, store, st)
        raise


# Відкіт зворотним порядком. Сюди веде ДВА шляхи: свіжий бізнес-збій (щойно вгорі)
# і відродження процесу, що помер посеред цього самого відкоту.
async def _roll_back(sid, steps, store, st):
    while st["cursor"] > 0:
        st["cursor"] -= 1
        await steps[st["cursor"]].comp()
        store.save(sid, st)                   # прогрес відкоту теж лягає на диск
    st["status"] = "compensated"; store.save(sid, st)
