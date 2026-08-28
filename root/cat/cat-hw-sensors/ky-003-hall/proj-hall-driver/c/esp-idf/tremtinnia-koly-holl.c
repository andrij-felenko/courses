#define DEBOUNCE_US 1000             // менший за найкоротший реальний період оберту

static volatile uint32_t pulses   = 0;
static volatile int64_t  lastEdge = 0;

static void IRAM_ATTR on_pulse(void *arg) {
    int64_t now = esp_timer_get_time();
    if (now - lastEdge < DEBOUNCE_US) return;  // надто рано → тремтіння, ігноруємо
    lastEdge = now;
    pulses++;
}
