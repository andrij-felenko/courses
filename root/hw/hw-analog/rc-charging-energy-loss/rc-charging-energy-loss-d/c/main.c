// Енергетичний баланс зарядки конденсатора від джерела сталої напруги.
// Усе в СІ: фаради, вольти, ом → джоулі та секунди.
typedef struct { float w_src, w_cap, w_heat, tau; } charge_budget_t;

charge_budget_t rc_charge_budget(float C, float V, float R)
{
    charge_budget_t b;
    b.w_cap  = 0.5f * C * V * V;   // осіло в конденсаторі
    b.w_heat = 0.5f * C * V * V;   // згоріло в резисторі — НЕ залежить від R
    b.w_src  = C * V * V;          // заплатило джерело = сума двох вище
    b.tau    = R * C;              // стала часу: лише вона залежить від R
    return b;
}
// rc_charge_budget(100e-6f, 5.0f, 100.0f):
//   w_cap = w_heat = 1.25 мДж,  w_src = 2.5 мДж,  tau = 10 мс
