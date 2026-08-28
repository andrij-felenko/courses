#include <stdint.h>
#include <stdio.h>
#include <math.h>     // floor()

// ── Опис радіо: усе так, як стоїть у даташиті ────────────────────────────
typedef struct {
    double carrier_hz;      // несна f₀, Гц     (напр. 2.4e9)
    double ppm;             // допуск кварцу, частин на мільйон (напр. 40)
    double signal_bw_hz;    // смуга сигналу B, Гц  (з потрібної швидкості)
    double guard_hz;        // захисний проміжок G на канал, Гц
    double rel_speed_ms;    // взаємна швидкість для Доплера, м/с (0 — нерухомі)
    double band_hz;         // уся доступна смуга діапазону, Гц
} radio_spec;

// ── Результат розрахунку ─────────────────────────────────────────────────
typedef struct {
    double drift_one_hz;    // дрейф несної з ОДНОГО боку (кварц + Доплер), Гц
    double slot_hz;         // повна ширина слота W = B + 2·Δf + G, Гц
    int    channels;        // скільки слотів влазить у смугу (округлення вниз)
    double overhead_frac;   // частка слота, що пішла НЕ на сигнал (0..1)
} channel_plan;
