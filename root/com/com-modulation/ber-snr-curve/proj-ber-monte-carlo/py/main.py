import numpy as np
import math

def simulate_ber(ebn0_db, target_errors=200, block=200_000,
                 max_bits=10**10, rng=None):
    """Емпірична BER для BPSK за одного Eb/N0.
    Крутить блоки бітів, доки не збере target_errors помилок
    (або не впреться в max_bits — щоб не зависнути на дні кривої)."""
    rng = rng or np.random.default_rng()
    g = 10 ** (ebn0_db / 10)           # Eb/N0 у рази
    sigma = 1.0 / math.sqrt(2 * g)     # σ² = N0/2 = 1/(2γ),  Eb = 1

    errors = total = 0
    while errors < target_errors and total < max_bits:
        bits = rng.integers(0, 2, block)                  # 1. джерело
        symb = 2 * bits - 1                                # 2. BPSK: 0→−1, 1→+1
        recv = symb + sigma * rng.standard_normal(block)   # 3. + шум AWGN
        decided = (recv > 0).astype(np.int8)               # 4. поріг у нулі
        errors += int(np.count_nonzero(decided != bits))   # 5. лічимо
        total += block
    return errors / total, errors, total
