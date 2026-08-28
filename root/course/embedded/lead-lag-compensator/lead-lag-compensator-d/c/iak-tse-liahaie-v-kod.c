// Компенсатор першого порядку (lead АБО lag) — різницеве рівняння.
// Коефіцієнти b0, b1, a1 рахують ОДИН раз із z, p і кроку dt
// (через білінійне перетворення). Тут — гарячий цикл керування.
typedef struct {
    float b0, b1, a1;   // коефіцієнти (з дискретизації C(s))
    float e_prev;       // попередня помилка
    float u_prev;       // попередній вихід
} comp_t;

float comp_step(comp_t *c, float e) {
    float u = c->b0 * e + c->b1 * c->e_prev - c->a1 * c->u_prev;
    c->e_prev = e;
    c->u_prev = u;
    return u;
}
