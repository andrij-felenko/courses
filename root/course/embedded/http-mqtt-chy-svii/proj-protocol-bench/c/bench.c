// Заміри трьох способів пакування на одному наборі значень (C99).
//
// На платі збирається з -DBENCH_USE_DWT: тоді лічильник тактів беруть із
// блоку DWT ядра Cortex-M і число в колонці — справжні такти. На робочій
// станції той самий код міряє час через clock() і показує наносекунди.
#include "receiver.h"
#include "telemetry.h"

#include <stdio.h>
#include <time.h>

#define BENCH_ITERATIONS 1000u

#if defined(BENCH_USE_DWT)

#define DEMCR      (*(volatile uint32_t *)0xE000EDFCu)
#define DWT_CTRL   (*(volatile uint32_t *)0xE0001000u)
#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)

static uint32_t g_start;

static void bench_setup(void)
{
    DEMCR |= (1u << 24);    // TRCENA — без нього блок DWT просто не тактується
    DWT_CYCCNT = 0;
    DWT_CTRL |= 1u;         // CYCCNTENA
}

static void bench_start(void)      { g_start = DWT_CYCCNT; }
static double bench_per_call(void) { return (double)(DWT_CYCCNT - g_start) / BENCH_ITERATIONS; }
static const char *bench_unit(void) { return "тактів"; }

#else

static clock_t g_start;

static void bench_setup(void) { }
static void bench_start(void) { g_start = clock(); }

static double bench_per_call(void)
{
    double seconds = (double)(clock() - g_start) / (double)CLOCKS_PER_SEC;
    return seconds * 1e9 / (double)BENCH_ITERATIONS;
}

static const char *bench_unit(void) { return "нс"; }

#endif

// volatile-приймач результату потрібен, щоб компілятор не викинув увесь цикл:
// без нього -O2 бачить, що значення нікуди не йде, і міряти стає нічого.
#define BENCH(label, expr)                                    \
    do {                                                      \
        volatile size_t sink = 0;                             \
        bench_start();                                        \
        for (unsigned i = 0; i < BENCH_ITERATIONS; i++) {     \
            sink = (expr);                                    \
        }                                                     \
        (void)sink;                                           \
        printf("  %-28s %8.1f %s\n", label, bench_per_call(), bench_unit()); \
    } while (0)

static void hex_dump(const char *label, const uint8_t *buf, size_t len)
{
    printf("  %s (%zu Б):", label, len);
    for (size_t i = 0; i < len; i++) {
        printf(" %02X", buf[i]);
    }
    printf("\n");
}

int main(void)
{
    const telemetry_sample_t sample = {
        .timestamp_s  = 1718000000u,
        .temp_centi_c = 2450,   // 24.50 °C
        .humidity_pct = 6020,   // 60.20 %
        .vbat_mv      = 3280    // 3.280 В
    };

    const char *host  = "iot.example.com";
    const char *token = "b7f3c1a9e5d24816b0c7f3a9e1d5b2c4a6f80931";
    const char *topic = "sensors/node42";

    char    http_buf[512];
    uint8_t mqtt_buf[128];
    uint8_t bin_buf[64];

    size_t http_len = build_http_post_request(&sample, host, token, http_buf, sizeof(http_buf));
    size_t mqtt_len = build_mqtt_publish_qos1(&sample, topic, 1, mqtt_buf, sizeof(mqtt_buf));
    size_t bin_len  = build_custom_binary_frame(&sample, 100, bin_buf, sizeof(bin_buf));

    if (http_len == 0 || mqtt_len == 0 || bin_len == 0) {
        fprintf(stderr, "не вдалося зібрати кадр: %zu / %zu / %zu\n", http_len, mqtt_len, bin_len);
        return 1;
    }

    printf("Розмір кадру з тими самими 10 байтами вимірів\n");
    printf("  HTTP POST + JSON   %4zu Б\n", http_len);
    printf("  MQTT PUBLISH QoS1  %4zu Б\n", mqtt_len);
    printf("  власний кадр       %4zu Б\n", bin_len);
    hex_dump("бінарний кадр", bin_buf, bin_len);
    printf("\n");

    bench_setup();
    printf("Вартість серіалізації (%u повторів)\n", BENCH_ITERATIONS);
    BENCH("HTTP POST + JSON",  build_http_post_request(&sample, host, token, http_buf, sizeof(http_buf)));
    BENCH("MQTT PUBLISH QoS1", build_mqtt_publish_qos1(&sample, topic, 1, mqtt_buf, sizeof(mqtt_buf)));
    BENCH("власний кадр",      build_custom_binary_frame(&sample, 100, bin_buf, sizeof(bin_buf)));
    printf("\n");

    // ---- приймальний бік: чотири перевірки на живих кадрах ----
    device_link_t link;
    device_link_init(&link);

    telemetry_sample_t got;
    uint16_t got_seq = 0;

    printf("Перевірки приймача\n");

    bin_len = build_custom_binary_frame(&sample, 100, bin_buf, sizeof(bin_buf));
    printf("  цілий кадр seq=100        -> %s\n",
           frame_status_name(device_link_accept(&link, bin_buf, bin_len, &got, &got_seq)));
    printf("    розібрано: ts=%lu t=%d.%02d h=%u.%02u vbat=%u мВ seq=%u\n",
           (unsigned long)got.timestamp_s,
           got.temp_centi_c / 100, got.temp_centi_c % 100,
           got.humidity_pct / 100, got.humidity_pct % 100,
           got.vbat_mv, got_seq);

    printf("  той самий кадр удруге     -> %s\n",
           frame_status_name(device_link_accept(&link, bin_buf, bin_len, &got, NULL)));

    bin_len = build_custom_binary_frame(&sample, 101, bin_buf, sizeof(bin_buf));
    bin_buf[6] ^= 0x01u;    // один перевернутий біт у полі часу — як завада в ефірі
    printf("  зіпсований біт            -> %s\n",
           frame_status_name(device_link_accept(&link, bin_buf, bin_len, &got, NULL)));

    bin_len = build_custom_binary_frame(&sample, 101, bin_buf, sizeof(bin_buf));
    bin_buf[0] = 0x55u;
    printf("  чужий синхробайт          -> %s\n",
           frame_status_name(device_link_accept(&link, bin_buf, bin_len, &got, NULL)));

    bin_len = build_custom_binary_frame(&sample, 101, bin_buf, sizeof(bin_buf));
    printf("  обрізана датаграма        -> %s\n",
           frame_status_name(device_link_accept(&link, bin_buf, bin_len - 3u, &got, NULL)));

    printf("  наступний кадр seq=101    -> %s\n",
           frame_status_name(device_link_accept(&link, bin_buf, bin_len, &got, &got_seq)));

    printf("\n  прийнято %u, відкинуто: короткі %u, синхробайт %u, тип %u, CRC %u, повтори %u\n",
           link.accepted, link.rejected_short, link.rejected_magic,
           link.rejected_type, link.rejected_crc, link.rejected_replay);

    return 0;
}
