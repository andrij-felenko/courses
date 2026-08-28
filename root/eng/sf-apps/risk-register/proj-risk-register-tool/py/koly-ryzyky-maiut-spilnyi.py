def extra_days(rng, correlated):
    """Три задачі можуть роздутися через брудні дані.
    НЕЗАЛЕЖНО: три окремі ризики, кожен p=0.30, +6 днів.
    СПІЛЬНИЙ КОРІНЬ: один ризик p=0.30, що б'є всі три РАЗОМ (+18 днів)."""
    if correlated:
        return 18.0 if rng.random() < 0.30 else 0.0
    total = 0.0
    for _ in range(3):
        if rng.random() < 0.30:
            total += 6.0
    return total

def sim_extra(correlated, n=100_000, seed=1):
    rng = random.Random(seed)
    return sorted(extra_days(rng, correlated) for _ in range(n))

for corr in (False, True):
    xs = sim_extra(corr)
    tag = "спільний корінь" if corr else "незалежні      "
    print(f"{tag}:  E={sum(xs)/len(xs):.1f}  "
          f"P80={pct(xs,80):.0f}  P95={pct(xs,95):.0f}  P99={pct(xs,99):.0f}")
