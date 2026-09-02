#include <stdio.h>

#include "fixedq16.h"
#include "iir_fixed.h"
#include "rawframe.h"
#include "sensor_si.h"

/* Кадр із вступу: шість байтів, знятих одним пакетним читанням по SPI
   з вихідних регістрів 12-бітного трьохосьового акселерометра. */
static const uint8_t kFrame[6] = { 0xF0, 0x0F, 0x00, 0x08, 0x40, 0x01 };

static void print_milli(const char *name, int32_t milli, const char *unit) {
    const long a = (milli < 0) ? -(long)milli : (long)milli;
    printf("    %-14s %s%ld.%03ld %s\n", name, (milli < 0) ? "-" : "",
           a / 1000L, a % 1000L, unit);
}

static void show_axes(const char *title, const int16_t raw[3]) {
    const vec3_mm_s2_t si = accel_frame12_to_si(raw, 0);
    const uint32_t mag = vec3_magnitude_mm_s2(si);

    printf("  %s\n", title);
    printf("    сирі відліки   X=%d Y=%d Z=%d\n", raw[0], raw[1], raw[2]);
    print_milli("X", si.x, "м/с^2");
    print_milli("Y", si.y, "м/с^2");
    print_milli("Z", si.z, "м/с^2");
    print_milli("модуль", (int32_t)mag, "м/с^2");
}

static void demo_frame(void) {
    int16_t wrong_order[3];
    int16_t no_sign[3];
    int16_t correct[3];
    unsigned i;

    puts("Розбір кадру 0xF0 0x0F 0x00 0x08 0x40 0x01:");

    /* Хиба перша: давач віддає молодший байт першим, а код склав слово
       так, ніби порядок зворотний. */
    rf_parse_be16(kFrame, wrong_order);
    show_axes("порядок байтів переплутано", wrong_order);

    /* Хиба друга: порядок правильний, але 12-бітне поле не розширене
       за знаком — від'ємні значення стали великими додатними. */
    for (i = 0u; i < 3u; ++i) {
        no_sign[i] = (int16_t)rf_u16_lsb_first(&kFrame[2u * i]);
    }
    show_axes("без знакового розширення", no_sign);

    /* Як треба: LSB-first плюс знакове розширення 12 бітів. */
    rf_parse_right_aligned(kFrame, 12u, correct);
    show_axes("правильний розбір", correct);

    /* Три способи розширення дають той самий результат. */
    {
        const uint16_t w = rf_u16_lsb_first(&kFrame[0]);
        printf("  знакове розширення 0x%04X: зсув=%d маска=%d SBFX=%d\n",
               (unsigned)w, rf_sign_extend_shift(w, 12u),
               rf_sign_extend_mask(w, 12u), rf_sign_extend_hw12(w));
    }
}

static void demo_filter(void) {
    iir_q16_t f;
    int16_t naive_state = 0;
    int n;

    iir_q16_init(&f, 3u); /* alpha = 1/8 */
    /* Перший відлік заряджає обидва фільтри нулем, далі подаємо 1000. */
    (void)iir_q16_update(&f, 0);

    puts("Мертва зона зсуву проти накопичувача Q16.16 (ціль 1000):");
    for (n = 0; n < 64; ++n) {
        (void)iir_naive_update(&naive_state, 1000, 3u);
        (void)iir_q16_update(&f, 1000);
    }
    printf("  наївний (стан у цілих): %d — застряг\n", naive_state);
    printf("  накопичувач Q16.16:     %ld\n", (long)iir_q16_value(&f));
}

static void demo_units(void) {
    puts("Масштабні коефіцієнти:");
    print_milli("TMP117", tmp117_to_mdeg_c(3200), "°C");
    print_milli("MCP9808", mcp9808_to_mdeg_c(400), "°C");
    print_milli("гіроскоп", gyro_lsb_to_mrad_s(28571, 0), "рад/с");
    print_milli("магнітометр", mag_lsb_to_nt(6842), "мкТл");

    puts("АЦП 12 біт при опорних 3300 мВ:");
    /* Свідома демонстрація переповнення: добуток обрізається по 2^16. */
    printf("    у 16 бітах    %u мВ\n",
           (unsigned)((uint16_t)(4095u * 3300u) / 4095u));
    printf("    у 32 бітах    %ld мВ\n", (long)adc12_to_mv(4095u, 3300u));
}

int main(void) {
    demo_frame();
    demo_filter();
    demo_units();
    return 0;
}
