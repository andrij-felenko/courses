typedef struct {
    float altitude_est;     /* Оцінена висота (м) */
    float velocity_est;     /* Оцінена вертикальна швидкість (м/с) */
    float accel_bias;       /* Оцінене зміщення нуля акселерометра */
    float kp;               /* Коефіцієнт корекції позиції */
    float ki;               /* Коефіцієнт корекції зміщення акселерометра */
} altimeter_fusion_t;

void altimeter_fusion_update(altimeter_fusion_t *f, float baro_alt, float accel_z_world, float dt) {
    /* 1. Апріорна екстраполяція за показами акселерометра */
    float accel_corrected = accel_z_world - f->accel_bias;
    f->altitude_est += f->velocity_est * dt + 0.5f * accel_corrected * dt * dt;
    f->velocity_est += accel_corrected * dt;

    /* 2. Розрахунок нев'язки з барометричним виміром */
    float error = baro_alt - f->altitude_est;

    /* 3. Апостеріорна корекція стану фільтра */
    f->altitude_est += error * f->kp * dt;
    f->velocity_est += error * f->ki * dt;
    f->accel_bias   -= error * (f->ki * 0.1f) * dt;
}
