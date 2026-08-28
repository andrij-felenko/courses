static void control_step(uint32_t now) {
    if (now - t_last_poll < T_POLL_MS) return;
    t_last_poll = now;

    float t = sensor_read_celsius();

    // Гістерезис визначає БАЖАНИЙ стан, не чіпаючи реле напряму.
    bool want = heater_on;                    // за замовчуванням — не міняти
    if (heater_on && t > setpoint + hyst)  want = false;   // перегрілися
    if (!heater_on && t < setpoint - hyst) want = true;    // охололи

    // А перемикання — лише якщо дозволяє мінімальний час.
    try_switch(want, now);
}

void loop(void) {
    uint32_t now = millis();
    control_step(now);      // швидко й завжди; тіло — раз на T_POLL_MS
    // ... тут же повільна петля: MQTT-звіт, прийом команд, mqtt_loop() ...
}
