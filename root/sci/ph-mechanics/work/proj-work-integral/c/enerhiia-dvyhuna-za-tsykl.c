/* Лічильник енергії реального часу.
   Кожен такт: energy += P·Δt = F·v·Δt. Знак зберігається сам —
   гальмівний такт (сила проти швидкості) дає від'ємний внесок. */
typedef struct {
    double energy_J;        /* накопичена робота, Дж */
} EnergyMeter;

static inline void meter_tick(EnergyMeter *m,
                              double force_N, double vel_mps, double dt_s) {
    m->energy_J += force_N * vel_mps * dt_s;
}
