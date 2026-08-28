from dataclasses import dataclass

@dataclass
class Window:
    lo: int        # індекс першої P у вікні
    hi: int        # індекс останньої P у вікні
    width: int     # hi - lo + 1; 0 = вікна нема (усе F)

# Знаходить НАЙШИРШЕ суцільне вікно P у pf_map[0..n-1].
def widest_window(pf_map: list[bool]) -> Window:
    best = Window(-1, -1, 0)
    cur_lo = -1                            # початок поточної смуги, -1 = поза смугою

    for i, cell in enumerate(pf_map):
        if cell:
            if cur_lo < 0:
                cur_lo = i                 # смуга щойно почалась
            w = i - cur_lo + 1
            if w > best.width:             # поточна побила рекорд — зберігаємо
                best.lo = cur_lo
                best.hi = i
                best.width = w
        else:
            cur_lo = -1                    # смуга обірвалась
    return best                            # best.width == 0, якщо жодної P
