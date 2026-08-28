void taskBlink(void *p)  { for(;;){ toggleLed(); vTaskDelay(500); } }   // блимати
void taskSensor(void *p) { for(;;){ readSensor();      // блокує 50 мс —
                                    vTaskDelay(1000); } }                //   та лише ЦЮ задачу
void taskComm(void *p)   { for(;;){ waitRequest();     // блокує, чекаючи —
                                    reply(); } }                         //   теж лише цю задачу

// у setup(): створюємо всі три
xTaskCreate(taskBlink,  "blink",  2048, NULL, 1, NULL);
xTaskCreate(taskSensor, "sensor", 2048, NULL, 1, NULL);
xTaskCreate(taskComm,   "comm",   4096, NULL, 1, NULL);
