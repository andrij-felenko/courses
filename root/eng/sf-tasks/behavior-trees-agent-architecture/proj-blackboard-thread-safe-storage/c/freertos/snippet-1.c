#include "FreeRTOS.h"
#include "semphr.h"
#include "event_groups.h"

// Структура даних сховища
typedef struct {
    float temperature;
    float humidity;
} SensorData;

static SensorData blackboard_data;
static SemaphoreHandle_t blackboard_mutex = NULL;
static EventGroupHandle_t blackboard_events = NULL;

#define EVENT_TEMP_UPDATED (1 << 0)

void Blackboard_Init(void) {
    blackboard_mutex = xSemaphoreCreateMutex();
    blackboard_events = xEventGroupCreate();
}

void Blackboard_WriteTemp(float new_temp) {
    if (xSemaphoreTake(blackboard_mutex, portMAX_DELAY) == pdTRUE) {
        blackboard_data.temperature = new_temp;
        xSemaphoreGive(blackboard_mutex);
        
        // Сповіщаємо підписників про оновлення
        xEventGroupSetBits(blackboard_events, EVENT_TEMP_UPDATED);
    }
}

float Blackboard_ReadTemp(void) {
    float temp = 0.0f;
    if (xSemaphoreTake(blackboard_mutex, portMAX_DELAY) == pdTRUE) {
        temp = blackboard_data.temperature;
        xSemaphoreGive(blackboard_mutex);
    }
    return temp;
}
