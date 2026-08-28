#define GUARD_US 800              // мертвий час, мкс: більший за пачку, менший за період

static volatile uint32_t pulses   = 0;
static volatile int64_t  lastEdge = 0;   // мітка часу зарахованого фронту, мкс

static void IRAM_ATTR on_edge(void *arg) {
  int64_t t = esp_timer_get_time();      // мкс від старту, 64 біти; безпечна в ISR
  if (t - lastEdge >= GUARD_US) {        // пройшло досить від попереднього фронту?
    pulses++;
    lastEdge = t;
  }
  // інакше — це дрижання того ж зубця, ігноруємо
}
