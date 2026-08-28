# ringbuf_model.py — еталон, звірка й звуження
import random
from collections import deque
from ringbuf_ffi import RingBuffer


def replay(ops, cap):
    """Прогнати послідовність через C і через модель.
    None — збіглося; інакше (вид розбіжності, пояснення)."""
    rb, model = RingBuffer(cap), deque(maxlen=cap)
    try:
        for op in ops:
            if op[0] == "push":
                was_full  = len(model) == cap
                displaced = rb.push(op[1])
                model.append(op[1])
                if displaced != was_full:
                    return ("push", f"C каже displaced={displaced}, модель — {was_full}")
            else:
                got  = rb.pop()
                want = model.popleft() if model else None
                if got != want:
                    return ("pop", f"C дало {got}, модель — {want}")
            if len(rb) != len(model):
                return ("len", f"C дало {len(rb)}, модель — {len(model)}")
    finally:
        rb.close()
    return None


def random_ops(rng, n):
    return [("push", rng.randrange(256)) if rng.random() < 0.6 else ("pop",)
            for _ in range(n)]
