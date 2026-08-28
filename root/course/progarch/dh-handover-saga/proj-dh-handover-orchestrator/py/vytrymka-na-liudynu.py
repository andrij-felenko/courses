import time
class WaitingForHuman(Exception):
    def __init__(self, until): self.until = until
DAY = 86_400

async def wait_for_owner(ctx):
    await post_claim_invite(ctx["home_id"], ctx["idem_key"])   # запросити (ідемпотентно)
    if await claim_accepted(ctx["home_id"]):
        return                                                 # уже підтвердили → завершено
    raise WaitingForHuman(time.time() + 7 * DAY)               # ще ні → паркуємось

async def on_claim(p, sid, steps):                             # підтвердили → уперед
    s = await p.load(sid)
    if s.status != "waiting": return                           # пізній клац — тиша
    s.status = "running"; await p.persist(s); await drive(p, sid, steps)

async def on_claim_deadline(p, sid, steps):                    # строк вийшов → розворот
    s = await p.load(sid)
    dl = s.deadline if s.deadline is not None else float("inf")   # None ≠ 0: не даємо «or» з'їсти нуль
    if s.status != "waiting" or time.time() < dl: return
    s.dir = "back"; s.status = "running"                       # cursor лишається на awaitClaim
    await p.persist(s); await drive(p, sid, steps)
