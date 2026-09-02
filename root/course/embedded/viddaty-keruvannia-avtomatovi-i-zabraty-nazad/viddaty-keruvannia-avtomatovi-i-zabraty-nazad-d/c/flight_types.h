#ifndef FLIGHT_TYPES_H
#define FLIGHT_TYPES_H

/* Спільні типи керівного тракту: команда на приводи, стан апарата
   та дві дрібниці, які потрібні всім модулям. */

typedef struct {
    float roll;     /* градуси, + = правий крен */
    float pitch;    /* градуси, + = кабрування */
    float yaw;      /* градуси/с, + = вправо */
    float throttle; /* 0.0 ... 1.0 */
} control_command_t;

typedef struct {
    float x;           /* м, уздовж початкового курсу */
    float y;           /* м, вліво від нього */
    float alt;         /* м над рівнем зльоту */
    float heading_deg; /* курс (напрямок носа), градуси */
    float airspeed;    /* м/с, повітряна швидкість */
} vehicle_state_t;

static inline float clampf(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

/* Зведення кута до діапазону -180…+180. */
static inline float wrap180(float deg) {
    while (deg > 180.0f) deg -= 360.0f;
    while (deg < -180.0f) deg += 360.0f;
    return deg;
}

#endif /* FLIGHT_TYPES_H */
