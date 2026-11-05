#include <Arduino_FreeRTOS.h>
#include <event_groups.h>

#define SENSOR_DATA_BIT (1 << 0)

EventGroupHandle_t blackboard_events;
volatile float shared_temperature;

void write_temperature(float temp) {
    noInterrupts();
    shared_temperature = temp;
    interrupts();
    
    xEventGroupSetBits(blackboard_events, SENSOR_DATA_BIT);
}

float read_temperature(void) {
    float temp_copy;
    noInterrupts();
    temp_copy = shared_temperature;
    interrupts();
    return temp_copy;
}
