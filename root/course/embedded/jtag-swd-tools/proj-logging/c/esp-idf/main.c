#define LOG_LOCAL_LEVEL  ESP_LOG_DEBUG   // поріг: нижче — ESP_LOG* зникає ще на збірці
#include "esp_log.h"                     // саме в такому порядку: поріг — ДО заголовка
#include "esp_rom_sys.h"                 // esp_rom_printf — можна навіть з паніки
#include <stdio.h>
#include <stdarg.h>

static const char *TAG = "app";
// рівень, час і мітку ESP_LOG* ставить сам: "I (1234) app: link up"

// ── Кільцевий буфер останніх рядків ──────────────────────────────────────
#define RING_N  32
static char ring[RING_N][80];       // фіксовані рядки — без купи, без фрагментації
static int  head = 0;

static void ring_push(const char *s) {
    snprintf(ring[head], sizeof(ring[0]), "%s", s);
    head = (head + 1) % RING_N;     // по колу: новий затирає найстаріший
}

// ── Перехоплення штатного виводу: рядок іде і в кільце, і далі в порт ─────
static vprintf_like_t next_out;     // попередній вивід — лишаємо як був

static int log_hook(const char *fmt, va_list ap) {
    char buf[80];
    va_list copy;
    va_copy(copy, ap);                             // ap віддамо далі неторканим
    vsnprintf(buf, sizeof(buf), fmt, copy);        // той самий рядок, що піде в порт
    va_end(copy);
    ring_push(buf);                                // завжди — у кільце
    return next_out(fmt, ap);
}

void log_init(void) { next_out = esp_log_set_vprintf(log_hook); }

// ── При аварії — висипати кільце від найстарішого ────────────────────────
void dump_ring(void) {
    esp_rom_printf(">>> останні слова:\n");
    for (int i = 0; i < RING_N; i++)
        esp_rom_printf("%s", ring[(head + i) % RING_N]);
}
