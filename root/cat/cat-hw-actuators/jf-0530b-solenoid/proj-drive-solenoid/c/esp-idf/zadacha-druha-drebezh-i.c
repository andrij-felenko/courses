#define SOL_PIN   GPIO_NUM_5
#define PULSE_MS  60               // тривалість самого клацання
#define REARM_MS  200              // мертвий час: раніше — не клацаємо повторно

static bool     sol_on       = false;
static uint32_t sol_start    = 0;
static uint32_t sol_last_end = 0;  // коли завершилося останнє клацання

// повертає true, якщо клацання прийнято; false — якщо відкинуто (ще рано)
bool solenoid_try_fire(void) {
    if (sol_on) return false;                             // уже клацаємо — не чіпати
    if (now_ms() - sol_last_end < REARM_MS) return false;  // ще не перезарядилися
    gpio_set_level(SOL_PIN, 1);
    sol_on    = true;
    sol_start = now_ms();
    return true;
}

void solenoid_update(void) {
    if (sol_on && (now_ms() - sol_start >= PULSE_MS)) {
        gpio_set_level(SOL_PIN, 0);
        sol_on       = false;
        sol_last_end = now_ms();   // запускаємо відлік перезарядки
    }
}
