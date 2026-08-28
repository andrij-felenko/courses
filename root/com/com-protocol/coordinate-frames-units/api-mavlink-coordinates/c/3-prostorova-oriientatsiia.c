typedef struct __mavlink_attitude_quaternion_t {
    uint32_t time_boot_ms;      /* Часовий штамп (мс) */
    float    q1;                /* Скалярна частина кватерніона w (cos(alpha/2)) */
    float    q2;                /* Векторна компонента x (вісь X_b) */
    float    q3;                /* Векторна компонента y (вісь Y_b) */
    float    q4;                /* Векторна компонента z (вісь Z_b) */
    float    rollspeed;         /* Кутова швидкість крену (rad/s) */
    float    pitchspeed;        /* Кутова швидкість тангажу (rad/s) */
    float    yawspeed;          /* Кутова швидкість рискання (rad/s) */
    float    repr_offset_q[4];  /* Кватерніон додаткового зміщення для підвісів камер */
} mavlink_attitude_quaternion_t;
