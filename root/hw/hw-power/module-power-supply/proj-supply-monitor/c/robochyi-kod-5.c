// Кроки послідовності живлення: вивід ключа + скільки чекати стабілізації.
typedef struct { uint32_t sw_pin; uint16_t settle_ms; } pwr_stage_t;

static const pwr_stage_t stages[] = {
    { LOADSW_SENSOR, 5  },   // 1) давач — малий кидок, вмикаємо першим
    { LOADSW_RADIO,  10 },   // 2) радіо — найненажерливіше, останнім
};
#define N_STAGES  (sizeof(stages) / sizeof(stages[0]))

static void all_loadsw_off(void) {
    for (uint32_t i = 0; i < N_STAGES; i++)
        gpio_write(stages[i].sw_pin, 0);   // погасити всі гілки
}

// Увімкнути підпорядковані вузли по черзі, звіряючи рейку після кожного.
// Повертає true, якщо вся послідовність піднялась без просідання.
bool power_bringup(void) {
    for (uint32_t i = 0; i < N_STAGES; i++) {
        gpio_write(stages[i].sw_pin, 1);           // увімкнути чергову гілку
        delay_ms(stages[i].settle_ms);             // дати конденсаторам зарядитись
        pwr_monitor_step(adc_read(CH_VREFINT));    // свіжий замір рейки

        if (!pwr_heavy_ok()) {          // рейка просіла від кидка цього вузла
            all_loadsw_off();           // ГОНКА: гасимо все, не лізем далі
            return false;               // хай викличник зачекає й пробує знову
        }
    }
    return true;                        // усі вузли підняті, рейка тримається
}
