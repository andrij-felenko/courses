def parity_encode(data):
    """Додати біт парності: сумарне число одиниць стає парним."""
    return data + [sum(data) % 2]

def recover_one_erasure(received):
    """Рівно одне None. Стертий біт = XOR решти (щоб знову було парно)."""
    i = received.index(None)
    received[i] = 0
    for b in received:
        if b is not None:
            received[i] ^= b
    return received
