// ─── тип повідомлення — єдиний «конверт» для будь-яких даних ─────────
enum MsgType : uint8_t { MSG_SAMPLE, MSG_BUTTON, MSG_SETMODE };
struct Msg {
    MsgType  type;
    int32_t  value;
};

// ─── черги — створюються один раз у setup() ──────────────────────────
static QueueHandle_t qEvents;    // fan-in: Sensor + Button → Control
static QueueHandle_t qActuator;  // Control → Actuator

// ─── PRODUCER 1: давач ────────────────────────────────────────────────
void taskSensor(void*) {
    for (;;) {
        Msg m{ MSG_SAMPLE, analogRead(PIN_A) };
        xQueueSend(qEvents, &m, portMAX_DELAY); // кладемо КОПІЮ — жодної спільної змінної
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// ─── PRODUCER 2: кнопка (fan-in у ту саму qEvents) ───────────────────
void taskButton(void*) {
    for (;;) {
        if (digitalRead(PIN_BTN) == LOW) {
            Msg m{ MSG_BUTTON, 1 };
            xQueueSend(qEvents, &m, pdMS_TO_TICKS(5));
            vTaskDelay(pdMS_TO_TICKS(50));      // debounce
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// ─── CONSUMER + PRODUCER: логіка керування ───────────────────────────
void taskControl(void*) {
    static int mode = 0;  // ← стан ПРИВАТНИЙ всередині задачі, не глобальний!
                          //   жодного м'ютекса не потрібно
    for (;;) {
        Msg m;
        xQueueReceive(qEvents, &m, portMAX_DELAY);  // спить, поки немає пошти
        switch (m.type) {
            case MSG_SAMPLE:
                if (m.value > 512) {
                    Msg cmd{ MSG_SAMPLE, 1 };
                    xQueueSend(qActuator, &cmd, pdMS_TO_TICKS(10));
                }
                break;
            case MSG_BUTTON:
                mode = (mode + 1) % 3;
                break;
            case MSG_SETMODE:
                mode = (int)m.value;
                break;
        }
    }
}

// ─── CONSUMER: виконавець на залізі ──────────────────────────────────
void taskActuator(void*) {
    for (;;) {
        Msg m;
        xQueueReceive(qActuator, &m, portMAX_DELAY);
        // Якщо реле на спільній шині SPI — лише тут беремо м'ютекс на шину
        // xSemaphoreTake(busMutex, portMAX_DELAY);
        digitalWrite(PIN_RELAY, m.value ? HIGH : LOW);
        // xSemaphoreGive(busMutex);
    }
}

// ─── Ініціалізація ────────────────────────────────────────────────────
void setup() {
    qEvents   = xQueueCreate(8, sizeof(Msg));
    qActuator = xQueueCreate(4, sizeof(Msg));
    configASSERT(qEvents && qActuator);

    xTaskCreate(taskSensor,   "Sensor",   2048, NULL, 2, NULL);
    xTaskCreate(taskButton,   "Button",   1024, NULL, 2, NULL);
    xTaskCreate(taskControl,  "Control",  2048, NULL, 3, NULL);
    xTaskCreate(taskActuator, "Actuator", 1536, NULL, 4, NULL);
}
void loop() { vTaskDelay(portMAX_DELAY); }
// ЖОДНОЇ спільної змінної між задачами — лише черги.
// Кожну задачу читаємо як окрему просту послідовну програму.
