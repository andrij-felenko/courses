// ── KY-039: читання пульсу з АЦП (ESP-IDF, adc_oneshot + FreeRTOS) ──

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char *TAG = "ky039";

#define PULSE_CH   ADC_CHANNEL_6    // GPIO34 — канал АЦП1 (переживає Wi-Fi)
#define SAMPLE_US  20000            // 50 Гц опитування

static adc_oneshot_unit_handle_t s_adc;

// -- крок 2: повільний нуль --
static float g_baseline = 0;
static const float BASE_ALPHA = 0.01f;

// -- крок 3: згладжування --
static float g_smooth = 0;
static const float SMOOTH_ALPHA = 0.35f;

// -- крок 4: пошук піків --
static float   g_prev     = 0;
static float   g_peak     = 0;
static int64_t g_lastBeat = 0;
static const float   MIN_AMP = 30.0f;    // 12-бітний АЦП: ~×4 від 10-бітного
static const int64_t MIN_GAP = 250000;   // глухе вікно, мкс

// -- крок 5: усереднення BPM --
#define N 5
static int64_t g_intervals[N] = {0};
static int     g_idx = 0;
static int64_t g_prevBeat = 0;
static bool    g_haveFirst = false;

static int64_t g_lastSample = 0;

static void report_beat(int64_t now);

static void pulse_task(void *arg) {
    int raw = 0;
    adc_oneshot_read(s_adc, PULSE_CH, &raw);
    g_baseline = raw;                        // старт нуля з першого відліку
    g_lastSample = esp_timer_get_time();

    while (1) {
        int64_t now = esp_timer_get_time();
        if (now - g_lastSample < SAMPLE_US) { // ще не час читати
            vTaskDelay(1);                    // віддати такт іншим задачам
            continue;
        }
        g_lastSample += SAMPLE_US;            // рівна сітка, не «= now»

        // -- крок 1: рівний відлік --
        adc_oneshot_read(s_adc, PULSE_CH, &raw);

        // -- крок 2: відняти повільний нуль --
        g_baseline += (raw - g_baseline) * BASE_ALPHA;
        float centered = raw - g_baseline;

        // -- крок 3: згладити --
        g_smooth += (centered - g_smooth) * SMOOTH_ALPHA;

        // -- крок 4: зловити удар --
        if (g_smooth > g_peak) g_peak = g_smooth;
        if (g_prev < 0 && g_smooth >= 0) {
            if (g_peak >= MIN_AMP && now - g_lastBeat >= MIN_GAP) {
                g_lastBeat = now;
                report_beat(now);             // -- крок 5 усередині --
            }
            g_peak = 0;
        }
        g_prev = g_smooth;
    }
}

// Викликається в мить кожного зарахованого удару.
static void report_beat(int64_t now) {
    if (!g_haveFirst) { g_prevBeat = now; g_haveFirst = true; return; }
    int64_t beatUs = now - g_prevBeat;
    g_prevBeat = now;
    if (beatUs < 250000 || beatUs > 2000000) return;   // явно хибний інтервал

    g_intervals[g_idx] = beatUs;
    g_idx = (g_idx + 1) % N;

    int64_t sum = 0; int cnt = 0;
    for (int i = 0; i < N; i++)
        if (g_intervals[i] > 0) { sum += g_intervals[i]; cnt++; }
    if (cnt == 0) return;
    int bpm = (int)(60000000LL / (sum / cnt));

    ESP_LOGI(TAG, "♥ удар   BPM ≈ %d", bpm);
}

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &s_adc));

    adc_oneshot_chan_cfg_t chan = {
        .atten    = ADC_ATTEN_DB_12,          // повний розмах входу
        .bitwidth = ADC_BITWIDTH_DEFAULT,     // 12 біт на ESP32
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s_adc, PULSE_CH, &chan));

    ESP_LOGI(TAG, "KY-039: поклади палець у щілину, тримай нерухомо.");
    xTaskCreate(pulse_task, "pulse", 4096, NULL, 5, NULL);
}
