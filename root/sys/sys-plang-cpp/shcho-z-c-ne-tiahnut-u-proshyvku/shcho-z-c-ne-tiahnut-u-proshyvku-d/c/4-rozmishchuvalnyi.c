#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Фіксований буфер пам'яті під структуру */
typedef struct {
    uint32_t sensor_id;
    float last_value;
} SensorDataC;

static uint8_t sensor_storage[sizeof(SensorDataC)];

/* Ініціалізація структури у статичній пам'яті */
SensorDataC* create_sensor_c(uint32_t id) {
    SensorDataC* s = (SensorDataC*)sensor_storage;
    s->sensor_id = id;
    s->last_value = 0.0f;
    return s;
}
