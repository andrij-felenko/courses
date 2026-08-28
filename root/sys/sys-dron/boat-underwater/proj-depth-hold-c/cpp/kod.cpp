#include <stdint.h>

/* --- Перерахунок тиску (Па) у глибину (м) з обнуленням на поверхні --- */
typedef struct {
    float rho_g;        /* ρ·g, Па/м: морська ≈ 10060, прісна ≈ 9810      */
    float p_surface;    /* абсолютний тиск на поверхні (тарування), Па    */
    float depth_f;      /* згладжена глибина, м (стан EMA)                */
    float ema_alpha;    /* коеф. згладжування 0<α≤1 (1 = без фільтра)     */
    uint8_t tared;      /* чи вже обнулено на поверхні                    */
} DepthSensor;

void depth_sensor_init(DepthSensor *d, float rho, float g, float ema_alpha)
{
    d->rho_g     = rho * g;          /* напр. 1025·9.81 для морської води */
    d->p_surface = 101325.0f;        /* доки не протаровано — стандартна атм. */
    d->depth_f   = 0.0f;
    d->ema_alpha = ema_alpha;
    d->tared     = 0;
}

/* Викликати РАЗ, поки апарат ще на поверхні й нерухомий. */
void depth_sensor_tare(DepthSensor *d, float p_abs)
{
    d->p_surface = p_abs;            /* цей тиск = «нуль глибини»          */
    d->depth_f   = 0.0f;
    d->tared     = 1;
}

/* Сирий абсолютний тиск (Па) → згладжена глибина (м, вниз додатна). */
float depth_from_pressure(DepthSensor *d, float p_abs)
{
    float depth_raw = (p_abs - d->p_surface) / d->rho_g;   /* h = (P−P₀)/(ρg) */
    /* EMA: тягне збережену глибину до свіжого виміру на частку α */
    d->depth_f += (depth_raw - d->depth_f) * d->ema_alpha;
    return d->depth_f;
}
