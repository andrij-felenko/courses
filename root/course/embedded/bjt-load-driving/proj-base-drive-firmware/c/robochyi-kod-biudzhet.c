#include <stdio.h>

typedef struct {
    const char *name;
    float von_or_rds;   // BJT: Vce(sat) [В]; MOSFET: Rds(on) [Ом]
    bool  is_mosfet;    // як трактувати von_or_rds
    float tr, tf;       // час фронтів [с] (для MOSFET сюди ж кладемо ефективні)
} switch_dev_t;

// Провідна втрата: BJT — D·Vce(sat)·Ic; MOSFET — D·Ic²·Rds(on).
static float p_cond(const switch_dev_t *d, float ic, float duty)
{
    if (d->is_mosfet) return duty * ic * ic * d->von_or_rds;
    else              return duty * d->von_or_rds * ic;
}

// Перемикальна втрата: ½·Vcc·Ic·(t_r+t_f)·f — однакова форма для обох.
static float p_sw(const switch_dev_t *d, float vcc, float ic, float f)
{
    return 0.5f * vcc * ic * (d->tr + d->tf) * f;
}

// Таблиця втрат по частоті для одного приладу.
void print_loss_table(const switch_dev_t *d, float vcc, float ic, float duty)
{
    static const float freqs[] = { 1e3f, 20e3f, 100e3f, 500e3f };
    printf("=== %s ===  (Vcc=%.0fВ Ic=%.2fА D=%.2f)\n", d->name, vcc, ic, duty);
    printf("  f, кГц | P_пров, Вт | P_перем, Вт | P_разом, Вт\n");
    for (unsigned i = 0; i < sizeof(freqs)/sizeof(freqs[0]); i++) {
        float pc = p_cond(d, ic, duty);
        float ps = p_sw(d, vcc, ic, freqs[i]);
        printf(" %6.0f | %10.3f | %11.3f | %11.3f\n",
               freqs[i] / 1e3f, pc, ps, pc + ps);
    }
}

// Рішення за чітким правилом: BJT простіший і дешевший, тож ЛИШАЄМО його,
// поки він вкладається в тепловий бюджет; на MOSFET переходимо лише тоді,
// коли BJT за бюджет вилітає (саме там перемикальна втрата його вбиває).
const char *choose_switch(const switch_dev_t *bjt, const switch_dev_t *mos,
                          float vcc, float ic, float duty, float f, float p_budget)
{
    float p_bjt = p_cond(bjt, ic, duty) + p_sw(bjt, vcc, ic, f);
    float p_mos = p_cond(mos, ic, duty) + p_sw(mos, vcc, ic, f);

    if (p_bjt <= p_budget) return bjt->name;   // BJT вкладається → простіший вибір
    if (p_mos <= p_budget) return mos->name;   // BJT вилетів, MOSFET тримається
    return "НІ ОДИН: обидва понад тепловий бюджет";
}
