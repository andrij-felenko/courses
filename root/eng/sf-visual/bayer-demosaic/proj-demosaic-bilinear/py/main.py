import numpy as np

def demosaic_bilinear(raw):
    """raw: 2-D uint8 RGGB-мозаїка -> out: (H, W, 3) uint8 RGB.
    Кожен із чотирьох типів пікселя — окремий зріз [початок::2]; сусідів
    беремо зсунутими зрізами й усереднюємо в int, аби не переповнити байт."""
    H, W = raw.shape
    r = raw.astype(np.int32)                      # у int, щоб суми не обгорнулись
    out = np.zeros((H, W, 3), np.int32)

    def avg(*a):                                  # чесне округлення: +half перед /n
        return (sum(a) + len(a) // 2) // len(a)

    # координатні зрізи внутрішньої області та її восьми сусідів
    c  = r[1:-1, 1:-1]
    up, dn = r[0:-2, 1:-1], r[2:, 1:-1]
    lf, rt = r[1:-1, 0:-2], r[1:-1, 2:]
    ul, ur = r[0:-2, 0:-2], r[0:-2, 2:]
    dl, dr = r[2:, 0:-2],  r[2:, 2:]
    o = out[1:-1, 1:-1]                            # вид на внутрішні пікселі виходу

    ey = np.arange(1, H - 1)[:, None] & 1          # парність рядка/стовпця
    ex = np.arange(1, W - 1)[None, :] & 1

    red   = (ey == 0) & (ex == 0)                  # червоний піксель
    grn_r = (ey == 0) & (ex == 1)                  # зелений на R-рядку
    grn_b = (ey == 1) & (ex == 0)                  # зелений на B-рядку
    blue  = (ey == 1) & (ex == 1)                  # синій піксель

    o[red]   = np.stack([c, avg(up, dn, lf, rt), avg(ul, ur, dl, dr)], -1)[red]
    o[grn_r] = np.stack([avg(lf, rt), c, avg(up, dn)], -1)[grn_r]
    o[grn_b] = np.stack([avg(up, dn), c, avg(lf, rt)], -1)[grn_b]
    o[blue]  = np.stack([avg(ul, ur, dl, dr), avg(up, dn, lf, rt), c], -1)[blue]
    return out.astype(np.uint8)
