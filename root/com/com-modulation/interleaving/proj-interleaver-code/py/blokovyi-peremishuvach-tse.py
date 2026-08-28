def block_perm(D: int, N: int) -> list[int]:
    """Позиція k в каналі -> звідки взяти символ у вхідному буфері."""
    return [(k % D) * N + (k // D) for k in range(D * N)]


def interleave(src: list, perm: list[int]) -> list:
    return [src[i] for i in perm]                 # dst[k] = src[perm[k]]


def deinterleave(chan: list, perm: list[int]) -> list:
    out = [None] * len(chan)
    for k, i in enumerate(perm):                  # кладемо символ назад на його місце
        out[i] = chan[k]
    return out
