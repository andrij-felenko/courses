// ─── антиприклад — НЕ робити так ────────────────────────────────────
volatile bool g_hasData   = false;   // ← перегін: Sensor пише, Control читає
volatile int  g_sample    = 0;       // ← перегін без м'ютекса
struct Cmd {
    bool  relayOn;
    uint8_t level;
} g_command;                         // ← перегін: Control пише, Actuator читає

// Якби боялись перегонів — довелось би ставити окремий м'ютекс
// на кожну зі змінних: SemaphoreHandle_t mx_data, mx_cmd;
// і брати/давати у кожній задачі. Це й є той «спагеті».

void taskSensor(void*) {
    for (;;) {
        g_sample  = analogRead(PIN_A);   // пише без захисту
        g_hasData = true;                // пише без захисту ← перегін!
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
void taskControl(void*) {
    for (;;) {
        if (g_hasData) {                 // читає без захисту ← перегін!
            g_hasData = false;
            g_command.relayOn = (g_sample > 512);   // пише без захисту
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
