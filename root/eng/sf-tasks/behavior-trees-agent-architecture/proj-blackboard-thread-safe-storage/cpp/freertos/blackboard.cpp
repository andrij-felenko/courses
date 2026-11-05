#include "FreeRTOS.h"
#include "semphr.h"
#include "event_groups.h"

class Blackboard {
private:
    struct SensorData {
        float temperature;
        float humidity;
    } data;
    
    SemaphoreHandle_t mutex;
    EventGroupHandle_t events;

public:
    static const EventBits_t TEMP_UPDATED = (1 << 0);

    Blackboard() {
        mutex = xSemaphoreCreateMutex();
        events = xEventGroupCreate();
    }

    void writeTemp(float temp) {
        if (xSemaphoreTake(mutex, portMAX_DELAY) == pdTRUE) {
            data.temperature = temp;
            xSemaphoreGive(mutex);
            xEventGroupSetBits(events, TEMP_UPDATED);
        }
    }

    float readTemp() {
        float temp = 0.0f;
        if (xSemaphoreTake(mutex, portMAX_DELAY) == pdTRUE) {
            temp = data.temperature;
            xSemaphoreGive(mutex);
        }
        return temp;
    }
    
    void waitForTempUpdate() {
        xEventGroupWaitBits(events, TEMP_UPDATED, pdTRUE, pdFALSE, portMAX_DELAY);
    }
};
