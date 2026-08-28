N_BLOCKS = 1024

erase_count = [0] * N_BLOCKS   # «пробіг» кожного блока
is_free     = [0] * N_BLOCKS   # 1 = блок стертий, готовий приймати запис

def pick_block_for_write():
    """Повертає індекс наймолодшого вільного блока, або -1, якщо вільних нема."""
    best = -1
    best_count = None

    for b in range(N_BLOCKS):
        if is_free[b] and (best_count is None or erase_count[b] < best_count):
            best_count = erase_count[b]
            best = b                  # цей поки що наймолодший

    return best                       # сюди й покладемо нові дані
