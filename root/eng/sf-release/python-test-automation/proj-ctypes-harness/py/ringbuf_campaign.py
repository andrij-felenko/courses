# ringbuf_campaign.py — ризиковані прогони живуть у власному процесі
import multiprocessing as mp, random, signal, sys
from ringbuf_model import replay, shrink, random_ops


def _campaign(tx, seed, cap, n):
    """Дитина. Спершу каже, що збирається робити, — потім робить."""
    tx.send(("план", {"seed": seed, "cap": cap, "n": n}))
    ops = random_ops(random.Random(seed), n)
    found = replay(ops, cap)
    if found is None:
        tx.send(("гаразд", None))
    else:
        kind, why = found
        tx.send(("розбіжність", {"чому": why, "приклад": shrink(ops, cap, kind)}))


def explain_exit(code):
    if code < 0:                                   # POSIX: убито сигналом
        try:    name = signal.Signals(-code).name
        except ValueError: name = "?"
        return f"убито сигналом {name} ({-code})"
    if sys.platform == "win32" and code > 0x7FFFFFFF:
        return f"аварійний статус 0x{code:08X}"
    return f"завершено з кодом {code}"


def run_campaign(seed, cap=8, n=20000, timeout=120.0):
    ctx = mp.get_context("spawn")       # чистий процес, нічого не успадковано
    rx, tx = ctx.Pipe(duplex=False)
    p = ctx.Process(target=_campaign, args=(tx, seed, cap, n))
    p.start()
    tx.close()                          # інакше rx ніколи не побачить кінця потоку

    said = []
    while True:
        if not rx.poll(timeout):
            p.kill(); p.join()
            raise TimeoutError(f"дитина мовчить {timeout} с; останнє: {said[-1:]}")
        try:
            said.append(rx.recv())
        except EOFError:
            break
    p.join()

    if p.exitcode != 0:
        raise AssertionError(
            f"C-бібліотека вбила процес: {explain_exit(p.exitcode)}\n"
            f"останнє, що дитина встигла сказати: {said[-1] if said else '—'}\n"
            f"відтворити: python -c \"from ringbuf_campaign import run_campaign;"
            f" run_campaign({seed}, {cap}, {n})\"")
    kind, payload = said[-1]
    assert kind != "розбіжність", f"{payload['чому']}\nконтрприклад: {payload['приклад']}"
