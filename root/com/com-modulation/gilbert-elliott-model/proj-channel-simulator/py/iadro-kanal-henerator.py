import random

def gilbert_elliott(n, p=0.001, r=0.1, e_g=0.0, e_b=0.4,
                    seed=None, warmup=10_000):
    """Потік каналу Гілберта–Елліота: на кожен біт — (стан_поганий, помилка).
       p: G→B,  r: B→G,  e_g/e_b: густота помилок у доброму/поганому стані."""
    rng = random.Random(seed)
    bad = rng.random() < p / (p + r)          # старт одразу зі сталого розподілу
    for _ in range(warmup):                   # +прогрів: добити перехідний режим
        bad = rng.random() >= r if bad else rng.random() < p
    for _ in range(n):
        err = rng.random() < (e_b if bad else e_g)   # монета помилки — за поточним станом
        yield bad, err
        bad = rng.random() >= r if bad else rng.random() < p   # монета переходу
