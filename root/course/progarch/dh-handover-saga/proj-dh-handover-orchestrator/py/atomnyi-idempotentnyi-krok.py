async def apply_step(p, saga, step, direction):
    key = f"{saga.id}:{step.name}:{direction}"             # ключ на крок І напрям
    action = step.run if direction == "forward" else step.compensate
    if action:
        await action({"home_id": saga.home_id, "idem_key": key})   # ефект; повтор — no-op на тому боці

    async with p.txn() as tx:                              # стан + подія — В ОДНІЙ транзакції
        if await p.seen(tx, key):
            return                                         # дубль → транзакція нічого не робить
        await p.mark(tx, key)
        saga.cursor += 1 if direction == "forward" else -1
        await p.save_in(tx, saga)
        await p.outbox(tx, {"saga": saga.id, "step": step.name, "dir": direction})
