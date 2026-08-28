// розкладка out: канали останні — спершу всі K чисел клітинки (0,0), потім (0,1)...
// клас k якоря a лежить ПІСЛЯ всіх п'ятірок: зсув B*5 + k (класи спільні на клітинку)
static det_t decode(const float *out, int cx, int cy, int a) {
    int base = (cy * S + cx) * K;     // початок вектора клітинки
    const float *t = out + base + a * 5;   // п'ятірка якоря a

    float bx = (cx + sigmoidf(t[0])) * STRIDE;   // центр X, пікселі
    float by = (cy + sigmoidf(t[1])) * STRIDE;   // центр Y, пікселі
    float bw = ANCHOR_W[a] * expf(t[2]);         // ширина, пікселі
    float bh = ANCHOR_H[a] * expf(t[3]);         // висота, пікселі
    float obj = sigmoidf(t[4]);                  // упевненість «тут об'єкт»

    // найкращий клас: max class-logit (softmax зберігає порядок, тож max logit = max p)
    const float *cl = out + base + B * 5;        // C class-logits клітинки
    int best = 0; float best_logit = cl[0];
    for (int k = 1; k < C; k++)
        if (cl[k] > best_logit) { best_logit = cl[k]; best = k; }
    float cls_p = sigmoidf(best_logit);          // ймовірність найкращого класу

    det_t d;
    d.x1 = bx - bw * 0.5f;  d.y1 = by - bh * 0.5f;   // центр+розмір → кути
    d.x2 = bx + bw * 0.5f;  d.y2 = by + bh * 0.5f;
    d.score = obj * cls_p;                        // обидва мають бути високі
    d.cls = best;
    return d;
}
