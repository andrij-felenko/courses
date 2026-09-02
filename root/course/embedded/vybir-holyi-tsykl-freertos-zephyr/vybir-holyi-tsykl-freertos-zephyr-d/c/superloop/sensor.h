#ifndef SUPERLOOP_SENSOR_H
#define SUPERLOOP_SENSOR_H

#include <stdbool.h>
#include <stdint.h>

/* Стан неблокуючого циклу вимірювання BME280 у режимі forced. */
typedef enum {
    SENSOR_IDLE = 0, /* чекає команди sensor_start()        */
    SENSOR_WAIT,     /* датчик міряє — просто виходимо      */
    SENSOR_READ,     /* час забрати сирі байти              */
    SENSOR_FAULT     /* шина або датчик не відповідають     */
} sensor_state_t;

typedef struct {
    sensor_state_t state;
    uint32_t started_ms;  /* коли запустили вимірювання      */
    int32_t  temp_c100;   /* останній вимір, сотые градуса   */
    uint32_t errors;      /* скільки разів шина впала        */
    uint8_t  retries;     /* невдач поспіль                  */
    /* Калібрування з ПЗП датчика (BME280 datasheet, розділ 4.2). */
    uint16_t dig_t1;
    int16_t  dig_t2;
    int16_t  dig_t3;
} sensor_t;

/* Піднімає I2C1, перевіряє ідентифікатор чипа, вичитує калібрування. */
bool sensor_init(sensor_t *s);

/* Запускає одне вимірювання. Повертатися по результат — справа sensor_poll(). */
void sensor_start(sensor_t *s, uint32_t now_ms);

/* Один крок автомата. true — з'явився новий вимір. Ніде не чекає в циклі. */
bool sensor_poll(sensor_t *s, uint32_t now_ms);

static inline int32_t sensor_temp_c100(const sensor_t *s) { return s->temp_c100; }

#endif /* SUPERLOOP_SENSOR_H */
