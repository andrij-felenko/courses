// ── Той самий шлюз на голому ESP-IDF. Тут не треба прикидатися Arduino:
//    плеєр кличе buzzerTone()/buzzerOff(), а ті йдуть просто в драйвер LEDC. ──
#include "driver/ledc.h"

#define BUZ_MODE   LEDC_LOW_SPEED_MODE
#define BUZ_TIMER  LEDC_TIMER_0
#define BUZ_CHAN   LEDC_CHANNEL_0
#define BUZ_DUTY   512     // 512 з 1024 (10 біт) = 50 %, чистий меандр

void buzzerTone(uint32_t freq)
{
    ledc_set_freq(BUZ_MODE, BUZ_TIMER, freq);      // частоту тримає ТАЙМЕР…
    ledc_set_duty(BUZ_MODE, BUZ_CHAN, BUZ_DUTY);   // …а шпаруватість — КАНАЛ
    ledc_update_duty(BUZ_MODE, BUZ_CHAN);          // без цього duty не поїде в залізо
}

void buzzerOff(void)
{
    ledc_set_duty(BUZ_MODE, BUZ_CHAN, 0);
    ledc_update_duty(BUZ_MODE, BUZ_CHAN);
}
// buzzerBegin() (ledc_timer_config + ledc_channel_config) — як у Кроці 1;
// плеєр, таблиця нот, сигнали, соніфікація — БЕЗ ЖОДНОЇ ЗМІНИ
