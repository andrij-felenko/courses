// такт debounce_clk ≈ 1 кГц (один такт = 1 мс); опис для GAL/CPLD
#define STABLE_TICKS 20             // 20 мс тиші → вхід вважаємо усталеним

static uint8_t cnt = 0;             // лічильник стабільності (тригери макрокомірки)
static uint8_t btn = 0;            // усунений від деренчання стан

void debounce_one(uint8_t btn_raw) {
    if (btn_raw == btn) {
        cnt = 0;                    // збігається з виходом — лічити нема чого
    } else if (++cnt >= STABLE_TICKS) {
        btn = btn_raw;              // 20 мс тримався новий рівень — приймаємо
        cnt = 0;
    }
}
