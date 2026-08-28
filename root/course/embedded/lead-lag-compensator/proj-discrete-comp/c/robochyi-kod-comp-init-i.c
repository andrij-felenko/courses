#include <math.h>

typedef struct {
    float b0, b1, a1;   // коефіцієнти різницевого рівняння (з C(s) через Тастіна)
    float e_prev;       // помилка з попереднього такту  (комірка z⁻¹ у чисельнику)
    float u_prev;       // вихід  з попереднього такту  (комірка z⁻¹ у знаменнику)
} comp_t;

// Ініціалізація: рахуємо коефіцієнти ОДИН раз із корнерів та кроку.
//   wz, wp — частоти нуля й полюса, рад/с (lead: wz<wp; lag: wz>wp)
//   dt     — крок дискретизації, с (1/частота керування)
//   K      — підсилення ланки (lead: 1.0; lag: wz/wp, див. каскад)
void comp_init(comp_t *c, float wz, float wp, float dt, float K)
{
    float cc = 2.0f / dt;            // множник білінійного перетворення

    float n0 = K * (1.0f + cc / wz); // чисельник: вільний член
    float n1 = K * (1.0f - cc / wz); // чисельник: член при z⁻¹
    float d0 =      1.0f + cc / wp;  // знаменник: вільний член
    float d1 =      1.0f - cc / wp;  // знаменник: член при z⁻¹

    c->b0 = n0 / d0;                 // нормуємо на d0 → коеф. при u[n] стає 1
    c->b1 = n1 / d0;
    c->a1 = d1 / d0;

    c->e_prev = 0.0f;
    c->u_prev = 0.0f;
}

// Гарячий такт: одне множення-додавання, два оновлення стану.
float comp_step(comp_t *c, float e)
{
    float u = c->b0 * e + c->b1 * c->e_prev - c->a1 * c->u_prev;
    c->e_prev = e;
    c->u_prev = u;
    return u;
}
