#include <Arduino.h>

QueueHandle_t q;                       // черга з відліками давача

void taskSensor(void *p) {             // виробник: читає й кладе в чергу
    for (;;) {
        int v = analogRead(34);        // умовний відлік давача
        xQueueSend(q, &v, portMAX_DELAY);   // копіює v у чергу, чекає за потреби
        vTaskDelay(pdMS_TO_TICKS(100));     // поступлива пауза ~100 мс
    }
}

void taskPrint(void *p) {              // споживач: забирає й друкує
    int v;
    for (;;) {
        if (xQueueReceive(q, &v, portMAX_DELAY) == pdTRUE)  // блокує, доки є дані
            Serial.printf("sensor = %d\n", v);
    }
}

void setup() {
    Serial.begin(115200);
    q = xQueueCreate(8, sizeof(int));  // 8 елементів по sizeof(int) байтів
    // обидві задачі — пріоритет 1, ядро лишаємо планувальникові:
    xTaskCreate(taskSensor, "sensor", 2048, NULL, 1, NULL);
    xTaskCreate(taskPrint,  "print",  2048, NULL, 1, NULL);
}

void loop() { vTaskDelay(pdMS_TO_TICKS(1000)); }   // loopTask нічого не робить
