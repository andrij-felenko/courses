// ESP32 Arduino-core. Рівний крок за апаратним таймером — проти джитера відліків.
volatile bool tick = false;
hw_timer_t* timer = nullptr;

void IRAM_ATTR onTimer() { tick = true; }   // лише прапорець — коротко й без блокувань

void setupSampler(uint32_t fs_hz) {
    timer = timerBegin(0, 80, true);          // 80 МГц/80 = 1 МГц → лік у мкс
    timerAttachInterrupt(timer, &onTimer, true);
    timerAlarmWrite(timer, 1000000UL / fs_hz, true);  // період = 1/fs у мкс
    timerAlarmEnable(timer);
}
