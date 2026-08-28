typedef struct {
    double temperature;        /* Абсолютна температура середовища, К (> 0) */
    double viscosity;          /* Динамічна в'язкість рідини, Па·с (> 0) */
    double particle_radius;    /* Гідродинамічний радіус частинки, м (> 0) */
    double particle_mass;      /* Маса частинки, кг (> 0) */
    double active_velocity;    /* Швидкість власного руху для активних частинок, м/с */
    double dt;                 /* Часовий крок інтегрування, с (> 0) */
    size_t trajectory_steps;   /* Загальна кількість кроків у кожній траєкторії */
    size_t ensemble_size;      /* Кількість частинок в ансамблі */
    unsigned int random_seed;  /* Базове зерно генератора випадкових чисел */
    BrownianSimMode mode;      /* Фізичний режим моделювання */
    int dimension;             /* Просторова розмірність: 1, 2 або 3 */
} BrownianConfig;
