#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t events = 0;

// викликається з задач, що можуть жити на РІЗНИХ ядрах
static void on_event(void) {
    taskENTER_CRITICAL(&lock);   // на мить забороняємо перемикання/друге ядро
    events++;                    // тепер інкремент неподільний
    taskEXIT_CRITICAL(&lock);    // відпускаємо якнайшвидше
}
