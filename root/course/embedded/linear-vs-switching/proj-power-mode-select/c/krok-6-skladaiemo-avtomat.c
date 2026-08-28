typedef enum { PWR_RUN, PWR_SLEEP } power_state_t;
static power_state_t g_power_state = PWR_RUN;

// RUN → SLEEP: перевести живлення в ощадний режим і заснути.
void power_enter_sleep(void)
{
    // 1) СПЕРШУ дати MCU другу, тиху опору (make-before-break).
    mcu_switch_to_ldo();

    // 2) Погасити зайві шини у ЗВОРОТНОМУ порядку залежностей.
    //    (Тут гасимо всі; якщо якась шина має жити уві сні — прибери її з циклу.)
    power_rails_off_reverse();

    // 3) Присипити головний buck у режим пропуску: тепер навантаження мале,
    //    перехід у PFM безпечний, струм спокою падає в рази.
    buck_set_mode_skip();

    g_power_state = PWR_SLEEP;
    esp_light_sleep_start();   // MCU дрімає на тихому LDO; buck ледь тліє
}

// SLEEP → RUN: розбудити живлення в правильному порядку, тоді віддати керування.
bool power_enter_run_from_sleep(void)
{
    // 1) Buck назад у повний PWM і шини за порядком, КОЖНА чекає PGOOD.
    if (!power_enter_run())
        return false;   // якась шина не піднялася — лишаємось на LDO, рапортуємо

    // 2) Головна шина підтверджена → безпечно повернути MCU на ефективний buck.
    mcu_switch_to_buck();

    g_power_state = PWR_RUN;
    return true;
}
