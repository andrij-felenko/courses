// ── KY-039 на STM32 (HAL): той самий тракт, 12-бітний АЦП ──

#include "main.h"                   // hadc1 і huart2 згенеровані CubeMX
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

extern ADC_HandleTypeDef  hadc1;    // канал на нозі, куди йде вихід S
extern UART_HandleTypeDef huart2;   // монітор порту

#define SAMPLE_MS 20                // 50 Гц опитування

// -- крок 2: повільний нуль --
static float g_baseline = 0;
static const float BASE_ALPHA = 0.01f;

// -- крок 3: згладжування --
static float g_smooth = 0;
static const float SMOOTH_ALPHA = 0.35f;

// -- крок 4: пошук піків --
static float    g_prev     = 0;
static float    g_peak     = 0;
static uint32_t g_lastBeat = 0;
static const float    MIN_AMP = 30.0f;   // 12-бітний АЦП: ~×4 від 10-бітного
static const uint32_t MIN_GAP = 250;     // глухе вікно, мс

// -- крок 5: усереднення BPM --
#define N 5
static uint32_t g_intervals[N] = {0};
static uint8_t  g_idx = 0;
static uint32_t g_prevBeat = 0;
static bool     g_haveFirst = false;

static uint32_t g_lastSample = 0;

static uint16_t adc_read(void) {
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    uint16_t v = (uint16_t)HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    return v;
}

static void report_beat(uint32_t now);

// Викликати з main() замість власного while(1).
void pulse_run(void) {
    const char *hello = "KY-039: поклади палець у щілину, тримай нерухомо.\r\n";
    HAL_UART_Transmit(&huart2, (uint8_t *)hello, strlen(hello), HAL_MAX_DELAY);
    HAL_Delay(50);
    g_baseline = adc_read();          // старт нуля з першого відліку
    g_lastSample = HAL_GetTick();

    while (1) {
        uint32_t now = HAL_GetTick();
        if (now - g_lastSample < SAMPLE_MS) continue;   // ще не час читати
        g_lastSample += SAMPLE_MS;                       // рівна сітка, не «= now»

        // -- крок 1: рівний відлік --
        uint16_t raw = adc_read();

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
                report_beat(now);           // -- крок 5 усередині --
            }
            g_peak = 0;
        }
        g_prev = g_smooth;
    }
}

// Викликається в мить кожного зарахованого удару.
static void report_beat(uint32_t now) {
    if (!g_haveFirst) { g_prevBeat = now; g_haveFirst = true; return; }
    uint32_t beatMs = now - g_prevBeat;
    g_prevBeat = now;
    if (beatMs < 250 || beatMs > 2000) return;   // явно хибний інтервал

    g_intervals[g_idx] = beatMs;
    g_idx = (g_idx + 1) % N;

    uint32_t sum = 0; uint8_t cnt = 0;
    for (uint8_t i = 0; i < N; i++)
        if (g_intervals[i] > 0) { sum += g_intervals[i]; cnt++; }
    if (cnt == 0) return;
    int bpm = (int)(60000UL / (sum / cnt));

    char line[48];
    int n = snprintf(line, sizeof line, "♥ удар   BPM ≈ %d\r\n", bpm);
    HAL_UART_Transmit(&huart2, (uint8_t *)line, n, HAL_MAX_DELAY);
}
