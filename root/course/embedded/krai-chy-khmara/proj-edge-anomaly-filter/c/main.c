/*
 * Прогін модуля на хості: синтетичний сигнал замість АЦП, друк рішень
 * замість радіо. Збірка — cc *.c -lm (rtos_tasks.c потребує FreeRTOS,
 * тож для хоста виключіть його: cc main.c edge_detector.c welford.c
 * ring_buffer.c telemetry_frame.c -lm).
 *
 * Сценарій навмисно містить усе, на чому модуль ламався б:
 * розігрів, стабільну норму, повільний дрейф, короткий викид,
 * залипання сигналу в константу й відмову давача.
 */
#include <math.h>
#include <stdio.h>

#include "edge_detector.h"
#include "telemetry_frame.h"

#define SAMPLE_COUNT   600u
#define PERIOD_MS      10u

/* xorshift32 — детермінований шум: прогін відтворюваний до біта. */
static uint32_t rng_state = 0x1234ABCDu;

static float noise_pm(float amplitude)
{
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 17;
    rng_state ^= rng_state << 5;
    const float unit = (float)(rng_state >> 8) / (float)(1u << 24);  /* [0, 1) */
    return (unit * 2.0f - 1.0f) * amplitude;
}

/* Напруга мережі: 230 В, шум +-0.1 В — саме той випадок, на якому
   наївна формула дисперсії втрачає значущі розряди. */
static float synth_sample(uint32_t k)
{
    if (k == 420u) {
        return NAN;                     /* обірваний вхід АЦП */
    }
    if (k >= 300u && k < 305u) {
        return 236.5f + noise_pm(0.1f); /* викид: стрибок на ~6 В */
    }
    if (k >= 500u) {
        return 231.0f;                  /* залипання: дисперсія падає в нуль */
    }

    const float drift = (k > 200u) ? 0.004f * (float)(k - 200u) : 0.0f;  /* нагрів */
    return 230.0f + drift + noise_pm(0.1f);
}

static const char *action_name(telemetry_action_t a)
{
    switch (a) {
        case DECISION_DISCARD:       return "DISCARD";
        case DECISION_HEARTBEAT:     return "HEARTBEAT";
        case DECISION_ANOMALY_ALARM: return "ALARM";
        default:                     return "?";
    }
}

static void print_frame(const telemetry_report_t *report,
                        const float *snapshot,
                        uint32_t snapshot_len)
{
    uint8_t frame[TELEMETRY_FRAME_MAX_SIZE];
    const size_t len = telemetry_frame_encode(report, snapshot, snapshot_len,
                                              frame, sizeof(frame));
    if (len == 0u) {
        printf("      кадр не спакувався\n");
        return;
    }

    printf("      кадр %zu Б (сирий знімок float зайняв би %zu Б), CRC 0x%04X:\n      ",
           len, (size_t)snapshot_len * sizeof(float),
           telemetry_crc16(frame, len - 2u));
    for (size_t i = 0; i < len; ++i) {
        printf("%02X", frame[i]);
        if ((i % 24u) == 23u && i + 1u < len) {
            printf("\n      ");
        }
    }
    printf("\n");
}

int main(void)
{
    edge_detector_t detector;
    edge_detector_init(&detector, 0u);

    uint32_t transmitted = 0;
    uint32_t alarms = 0;

    for (uint32_t k = 0; k < SAMPLE_COUNT; ++k) {
        const uint32_t now_ms = k * PERIOD_MS;
        const float sample = synth_sample(k);

        const telemetry_report_t report = edge_detector_process(&detector, sample, now_ms);
        if (report.action == DECISION_DISCARD) {
            continue;
        }

        transmitted++;
        if (report.action == DECISION_ANOMALY_ALARM) {
            alarms++;
        }

        printf("k=%3u  t=%5u мс  %-9s  x=%8.3f  mean=%8.3f  sigma=%6.4f  z=%5.2f%s\n",
               k, now_ms, action_name(report.action),
               (double)report.value, (double)report.running_mean,
               (double)report.running_stddev, (double)report.z_score,
               report.sensor_fault ? "  [відмова давача]" : "");

        if (report.action == DECISION_ANOMALY_ALARM) {
            float snapshot[RING_BUFFER_CAPACITY];
            const uint32_t n = edge_detector_snapshot(&detector, snapshot,
                                                      RING_BUFFER_CAPACITY);
            printf("      передісторія %u вибірок: %.3f ... %.3f\n",
                   n, (double)snapshot[0], (double)snapshot[n ? n - 1u : 0u]);
            print_frame(&report, snapshot, n);
        }
    }

    printf("\nВибірок: %u.  В ефір пішло: %u (%.1f%%), з них тривог: %u.\n",
           SAMPLE_COUNT, transmitted,
           100.0 * (double)transmitted / (double)SAMPLE_COUNT, alarms);
    return 0;
}
