// результат пошуку для одного пікселя
typedef struct {
    uint32_t best_cost;     // найменший SAD
    uint32_t second_cost;   // другий найменший SAD (поза околом переможця)
    int      best_d;
} match_t;

#define INVALID_DISP 0xFF   // позначка «диспаритет невідомий»

// у внутрішньому циклі, замість простого порівняння, ведемо ДВА мінімуми:
//   if (cost < best_cost) { second_cost = best_cost; best_cost = cost; best_d = d; }
//   else if (cost < second_cost) second_cost = cost;
// (другий мінімум беремо лише поза ±1 від best_d — сусідні d природно близькі)

static uint8_t accept_or_reject(const match_t *m)
{
    // унікальність: наскільки другий претендент гірший за переможця, у відсотках.
    // якщо другий лише трохи гірший — пік нечіткий, збіг ненадійний.
    // (best+1) у знаменнику страхує від ділення на нуль на ідеальному збігу.
    uint32_t margin = m->second_cost - m->best_cost;
    if (margin * 100 < UNIQUE_PCT * (m->best_cost + 1))
        return INVALID_DISP;            // надто близькі претенденти — не віримо

    return (uint8_t)m->best_d;
}
