# розкладка out: канали останні — спершу всі K чисел клітинки (0,0), потім (0,1)...
# клас k якоря a лежить ПІСЛЯ всіх п'ятірок: зсув B*5 + k (класи спільні на клітинку)
def decode(out, cx, cy, a):
    base = (cy * S + cx) * K          # початок вектора клітинки
    t = base + a * 5                  # п'ятірка якоря a

    bx = (cx + sigmoid(out[t + 0])) * STRIDE   # центр X, пікселі
    by = (cy + sigmoid(out[t + 1])) * STRIDE   # центр Y, пікселі
    bw = ANCHOR_W[a] * math.exp(out[t + 2])    # ширина, пікселі
    bh = ANCHOR_H[a] * math.exp(out[t + 3])    # висота, пікселі
    obj = sigmoid(out[t + 4])                  # упевненість «тут об'єкт»

    # найкращий клас: max class-logit (softmax зберігає порядок, тож max logit = max p)
    cl = base + B * 5                          # C class-logits клітинки
    best, best_logit = 0, out[cl]
    for k in range(1, C):
        if out[cl + k] > best_logit:
            best_logit, best = out[cl + k], k
    cls_p = sigmoid(best_logit)                # ймовірність найкращого класу

    return Det(
        x1=bx - bw * 0.5, y1=by - bh * 0.5,    # центр+розмір → кути
        x2=bx + bw * 0.5, y2=by + bh * 0.5,
        score=obj * cls_p,                     # обидва мають бути високі
        cls=best,
    )
