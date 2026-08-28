#define GUARD 0xDEADBEEFu
static uint8_t  work[2048];
static volatile uint32_t guard = GUARD;   // вартовий ОДРАЗУ за межею ділянки

static inline bool guard_ok(void) { return guard == GUARD; }

// у діагностичному циклі (наприклад, watchdog-задача):
if (!guard_ok()) {
    esp_rom_printf("guard corrupted: overflow near 'work'\n");
    abort();
}
