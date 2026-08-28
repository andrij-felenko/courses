#include <stdint.h>

/* Оголошення структури кадру HIL_SENSOR мовою C */
typedef struct __mavlink_hil_sensor_t {
    uint64_t time_usec;        /* Монотонний час симуляції у мікросекундах */
    float xacc;                /* Акселерометр X (м/с²) у Body Frame */
    float yacc;                /* Акселерометр Y (м/с²) у Body Frame */
    float zacc;                /* Акселерометр Z (м/с²) у Body Frame */
    float xgyro;               /* Гіроскоп X (рад/с) навколо осі Roll */
    float ygyro;               /* Гіроскоп Y (рад/с) навколо осі Pitch */
    float zgyro;               /* Гіроскоп Z (рад/с) навколо осі Yaw */
    float xmag;                /* Магнітометр X (Гаус) */
    float ymag;                /* Магнітометр Y (Гаус) */
    float zmag;                /* Магнітометр Z (Гаус) */
    float abs_pressure;        /* Абсолютний барометричний тиск (гПа / мілібари) */
    float diff_pressure;       /* Диференційний тиск трубки Піто (гПа) */
    float pressure_alt;        /* Розрахована барометрична висота (метри) */
    float temperature;         /* Температура сенсорного модуля (°C) */
    uint32_t fields_updated;   /* Бітова маска оновлених сенсорів у поточному кадрі */
    uint8_t id;                /* Ідентифікатор комплексу сенсорів (0 для основного блоку) */
} mavlink_hil_sensor_t;
