// --- Стан вузла (усе, чим він живе) ---
static float  g_temp        = 0.0f;    // останнє показання давача, °C
static float  g_setpoint    = 21.0f;   // поріг: нижче — гріти. Заводське значення
static bool   g_heater_on   = false;   // поточний стан реле
static bool   g_net_up      = false;   // чи є зв'язок із брокером
static uint32_t t_last_report = 0;     // коли востаннє звітували, мс

#define REPORT_PERIOD_MS  10000        // звіт раз на 10 с
#define HYSTERESIS        0.3f         // «мертва зона» навколо порога, °C

// --- ШВИДКА ПЕТЛЯ: знімання + рішення (жодної мережі) ---
static void control_step(void) {
    g_temp = sensor_read_celsius();    // читаємо давач по I2C

    // Автономне правило з гістерезисом: щоб реле не деренчало на межі
    if (!g_heater_on && g_temp < g_setpoint - HYSTERESIS) {
        g_heater_on = true;
        relay_set(true);               // локальна дія — дротом, миттєво
    } else if (g_heater_on && g_temp > g_setpoint + HYSTERESIS) {
        g_heater_on = false;
        relay_set(false);
    }
}

// --- ПОВІЛЬНА ПЕТЛЯ: звіт (тільки якщо є зв'язок) ---
static void report_step(uint32_t now) {
    if (now - t_last_report < REPORT_PERIOD_MS) return;  // ще не час
    t_last_report = now;
    if (!g_net_up) return;             // зв'язку нема — просто пропускаємо звіт

    char payload[64];
    snprintf(payload, sizeof payload,
             "{\"temp\":%.1f,\"heater\":%s,\"set\":%.1f}",
             g_temp, g_heater_on ? "true" : "false", g_setpoint);
    // стан → retain=1: хто підключиться пізніше, одразу побачить поточне
    mqtt_publish("home/livingroom/thermostat/state", payload, /*qos*/0, /*retain*/1);
}

void loop(void) {
    uint32_t now = millis();
    control_step();                    // крутиться щоразу — швидко й завжди
    report_step(now);                  // спрацьовує зрідка, за таймером
    mqtt_loop();                       // обслуговує з'єднання, не блокує
}
