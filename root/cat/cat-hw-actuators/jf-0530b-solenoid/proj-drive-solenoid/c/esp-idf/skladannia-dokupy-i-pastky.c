// ── Повний драйвер JF-0530B на ESP-IDF: клацання АБО «втягнути-й-тримати» ───
#include "driver/ledc.h"
#include "esp_timer.h"

#define SOL_PIN     GPIO_NUM_5      // ШІМ-здатна ніжка → затвор MOSFET / вхід INx ULN2003
#define PEAK_MS     60              // повний струм на втягування
#define HOLD_DUTY   90              // ШІМ-утримання (0..255), добрати під примірник
#define REARM_MS    200             // мертвий час між клацаннями (дребезг + фізика + тепло)
#define MAX_ON_MS   30000           // абсолютна стеля утримання (страхувальник від бага)

typedef enum { SOL_IDLE, SOL_PEAK, SOL_HOLD } sol_state_t;
static sol_state_t sol_state    = SOL_IDLE;
static uint32_t    sol_start    = 0;   // мить старту поточного вмикання
static uint32_t    sol_last_end = 0;   // мить кінця останнього вмикання
static bool        hold_mode    = false; // true → після PEAK лишаємось у HOLD

static uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }

static void sol_duty(uint32_t duty) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void solenoid_setup(void) {         // таймер LEDC на 25 кГц + канал на ніжці (див. вище)
    ledc_timer_config_t t = {
        .speed_mode = LEDC_LOW_SPEED_MODE, .timer_num = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT, .freq_hz = 25000, .clk_cfg = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&t));
    ledc_channel_config_t c = {
        .gpio_num = SOL_PIN, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0, .duty = 0, .hpoint = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&c));
}

static bool sol_begin(bool hold) {  // спільний старт обох режимів
    if (sol_state != SOL_IDLE) return false;
    if (now_ms() - sol_last_end < REARM_MS) return false;
    sol_duty(255);                  // повний кидок
    sol_state = SOL_PEAK; hold_mode = hold; sol_start = now_ms();
    return true;
}

bool solenoid_pulse(void) { return sol_begin(false); }  // одиночне клацання
bool solenoid_hold(void)  { return sol_begin(true);  }  // втягнути й ТРИМАТИ

void solenoid_release(void) {
    sol_duty(0);
    if (sol_state != SOL_IDLE) sol_last_end = now_ms();
    sol_state = SOL_IDLE;
}

void solenoid_update(void) {        // кликати щопрохід задачі
    switch (sol_state) {
        case SOL_PEAK:
            if (now_ms() - sol_start >= PEAK_MS) {
                if (hold_mode) { sol_duty(HOLD_DUTY); sol_state = SOL_HOLD; }
                else           { solenoid_release(); }   // одиночний клац завершено
            }
            break;
        case SOL_HOLD:
            if (now_ms() - sol_start >= MAX_ON_MS)       // стеля: тримають задовго — рубаємо
                solenoid_release();
            break;
        default: break;
    }
}
