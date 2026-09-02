/*
 * Модель об'єкта керування для демонстрації: вертикальний канал
 * мультикоптера. Вимірювана величина — швидкість набору висоти [м/с],
 * керування — нормований хід газу [0..1].
 */
#ifndef PLANT_H
#define PLANT_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    float altitude;        /* м — інтеграл швидкості, для наочності звіту */
    float climb_rate;      /* м/с — істинна швидкість набору */
    float hover_throttle;  /* хід газу, на якому тяга дорівнює вазі */
    float thrust_gain;     /* м/с² на одиницю ходу газу понад завислість */
    float drag;            /* 1/с — аеродинамічне гальмування */
    float gust;            /* м/с² — стале збурення (порив вітру) */
    float noise;           /* м/с — згладжений шум давача */
    uint32_t rng;          /* стан генератора шуму */
} plant_t;

void plant_init(plant_t *plant, float hover_throttle);

/* Один крок інтегрування; повертає нову істинну швидкість набору. */
float plant_step(plant_t *plant, float throttle, float dt);

/*
 * Відлік давача: істинна швидкість плюс згладжений шум.
 * `fault` імітує зрив обміну на шині — тоді повертається NaN.
 */
float plant_sample(plant_t *plant, bool fault);

#endif /* PLANT_H */
