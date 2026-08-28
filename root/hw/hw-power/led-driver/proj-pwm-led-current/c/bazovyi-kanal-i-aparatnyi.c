#include "driver/ledc.h"
#include "esp_err.h"

// ── Параметри ШІМ-димінгу ───────────────────────────────────────────────
#define DIM_TIMER      LEDC_TIMER_0
#define DIM_MODE       LEDC_LOW_SPEED_MODE     // low-speed group: є на всіх ESP32
#define DIM_RES        LEDC_TIMER_12_BIT       // 12 біт → duty 0..4095
#define DIM_FREQ_HZ    20000                   // 20 кГц: вище чутного й видимого
#define DIM_DUTY_MAX   ((1 << 12) - 1)         // 4095

// Один фізичний канал димінгу: ніжка EN драйвера ↔ канал LEDC.
typedef struct {
    int              gpio;      // ніжка EN/PWM драйвера струму
    ledc_channel_t   channel;   // апаратний канал LEDC
} dim_ch_t;

// Підняти спільний таймер (робимо раз перед каналами).
static void dim_timer_init(void) {
    ledc_timer_config_t tcfg = {
        .speed_mode      = DIM_MODE,
        .timer_num       = DIM_TIMER,
        .duty_resolution = DIM_RES,
        .freq_hz         = DIM_FREQ_HZ,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tcfg));
}

// Прив'язати канал до ніжки; старт із нуля (світлодіод погашено).
static void dim_channel_init(const dim_ch_t *ch) {
    ledc_channel_config_t ccfg = {
        .speed_mode = DIM_MODE,
        .channel    = ch->channel,
        .timer_sel  = DIM_TIMER,
        .gpio_num   = ch->gpio,
        .duty       = 0,
        .hpoint     = 0,        // фаза вмикання (див. синхронізацію нижче)
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ccfg));
}

// Увімкнути апаратну службу fade (раз на весь застосунок).
static void dim_fade_service_init(void) {
    ESP_ERROR_CHECK(ledc_fade_func_install(0));   // 0 = без своїх прапорців ISR
}

// Плавний перехід каналу до цільового duty за задану кількість мілісекунд.
// Залізо саме прокручує duty; процесор вільний.  NO_WAIT = не блокуємось.
static void dim_fade_to(const dim_ch_t *ch, uint32_t target_duty, int ms) {
    if (target_duty > DIM_DUTY_MAX) target_duty = DIM_DUTY_MAX;
    ESP_ERROR_CHECK(ledc_set_fade_with_time(DIM_MODE, ch->channel, target_duty, ms));
    ESP_ERROR_CHECK(ledc_fade_start(DIM_MODE, ch->channel, LEDC_FADE_NO_WAIT));
}
