QueueHandle_t    q;          // черга відліків давача
SemaphoreHandle_t busMutex;  // замок на спільну шину дисплея

void taskSensor(void *p) {                 // ВИРОБНИК
    for (;;) {
        int v = readSensor();
        xQueueSend(q, &v, portMAX_DELAY);      // безпечно передали відлік (копія)
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void taskLog(void *p) {                    // СПОЖИВАЧ
    for (;;) {
        int v;
        xQueueReceive(q, &v, portMAX_DELAY);            // чекаємо й беремо (блок)
        xSemaphoreTake(busMutex, portMAX_DELAY);        // ← зайняли спільну шину
        writeToDisplay(v);                              //   працюємо з нею
        xSemaphoreGive(busMutex);                       // ← звільнили шину
    }
}
