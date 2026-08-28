// Глобальна яскравість 0..8: скільки з 8 під-тиків розряд світиться.
volatile uint8_t brightness = 8;   // 8 = повна; 4 = половина; 1 = ледь-ледь
static   uint8_t subtick    = 0;

// Тепер таймер тикає у 8 разів частіше (8 під-тиків на розряд):
// 400 Гц × 8 = 3200 Гц, період ≈ 0.31 мс.
void refresh_isr_dim(void)
{
    if (subtick == 0) {                 // початок вікна розряду — перемалювати
        all_digits_off();
        uint8_t seg = frame[cur];
        if (dots & (1u << cur)) seg |= (1u << 7);
        put_segments(seg);
        digit_on(cur);                  // відкрили розряд
    }
    if (subtick == brightness)          // відсвітив свою частку вікна —
        all_digits_off();               // гасимо достроково (решту вікна темно)

    if (++subtick >= 8) {               // вікно скінчилось
        subtick = 0;
        cur = (cur + 1) & 3;           // наступний розряд
    }
}
