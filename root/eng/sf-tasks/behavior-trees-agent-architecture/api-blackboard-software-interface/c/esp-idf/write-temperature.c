#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

#define SENSOR_DATA_BIT (1 << 0)

static EventGroupHandle_t blackboard_events;
static float shared_temperature;
static portMUX_TYPE spinlock = portMUX_INITIALIZER_UNLOCKED;

void write_temperature(float temp) {
    taskENTER_CRITICAL(&spinlock);
    shared_temperature = temp;
    taskEXIT_CRITICAL(&spinlock);
    xEventGroupSetBits(blackboard_events, SENSOR_DATA_BIT);
}

float read_temperature(void) {
    float temp_copy;
    taskENTER_CRITICAL(&spinlock);
    temp_copy = shared_temperature;
    taskEXIT_CRITICAL(&spinlock);
    return temp_copy;
}
