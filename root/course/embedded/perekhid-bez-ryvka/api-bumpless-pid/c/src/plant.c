#include "plant.h"

#include <math.h>

/* Лінійний конгруентний генератор: детермінований, без залежностей. */
static float plant_white(plant_t *plant)
{
    plant->rng = plant->rng * 1664525u + 1013904223u;
    return (float)((plant->rng >> 8) & 0xFFFFu) / 32767.5f - 1.0f;
}

void plant_init(plant_t *plant, float hover_throttle)
{
    plant->altitude = 0.0f;
    plant->climb_rate = 0.0f;
    plant->hover_throttle = hover_throttle;
    plant->thrust_gain = 12.0f;   /* повний хід газу дає ~12 м/с² надлишку */
    plant->drag = 0.8f;           /* усталена швидкість = 15 м/с на одиницю ходу */
    plant->gust = 0.0f;
    plant->noise = 0.0f;
    plant->rng = 0x13579BDFu;
}

float plant_step(plant_t *plant, float throttle, float dt)
{
    float accel;

    accel = (throttle - plant->hover_throttle) * plant->thrust_gain
            - plant->drag * plant->climb_rate
            + plant->gust;

    plant->climb_rate += accel * dt;
    plant->altitude += plant->climb_rate * dt;

    /* Земля: нижче нуля апарат не опускається, швидкість гасне. */
    if (plant->altitude < 0.0f) {
        plant->altitude = 0.0f;
        if (plant->climb_rate < 0.0f) {
            plant->climb_rate = 0.0f;
        }
    }
    return plant->climb_rate;
}

float plant_sample(plant_t *plant, bool fault)
{
    /* Шум фільтрованої оцінки швидкості — вузькосмуговий, не білий. */
    plant->noise = 0.9f * plant->noise + 0.1f * (0.01f * plant_white(plant));

    if (fault) {
        return NAN;
    }
    return plant->climb_rate + plant->noise;
}
