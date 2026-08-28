import math

# Перетин кола (центр c, радіус L) з відрізком A→B.
# Якщо є корінь ПОПЕРЕДУ (більший) у межах [0,1] — повертає його,
# інакше None (перетину на цьому відрізку немає).
def seg_circle_hit(c, L, A, B):
    dx, dy = B[0] - A[0], B[1] - A[1]          # d = B − A
    fx, fy = A[0] - c[0], A[1] - c[1]          # f = A − c

    a = dx * dx + dy * dy                       # a = d·d
    b = 2.0 * (fx * dx + fy * dy)               # b = 2 f·d
    cc = fx * fx + fy * fy - L * L              # c = f·f − L²

    if a < 1e-9:
        return None                             # вироджений (нульовий) відрізок

    disc = b * b - 4.0 * a * cc
    if disc < 0.0:
        return None                             # коло не дістає відрізка (дірка)

    sq = math.sqrt(disc)
    t2 = (-b + sq) / (2.0 * a)                  # БІЛЬШИЙ корінь — попереду за рухом

    if 0.0 <= t2 <= 1.0:                         # і лежить у межах відрізка?
        return t2
    return None                                 # попереднього перетину на відрізку нема
