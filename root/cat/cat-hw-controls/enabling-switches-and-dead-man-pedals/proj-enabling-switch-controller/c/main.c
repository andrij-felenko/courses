#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "enabling_switch.h"
#include "vigilance_control.h"

// Апаратна імітація сигналів GPIO для тестування
static bool sim_gpio_ch1 = false;
static bool sim_gpio_ch2 = false;
static bool safety_relay_output = false;

/**
 * @brief Імітація зчитування фізичних ніжок GPIO мікроконтролера.
 */
static void Read_HAL_GPIO(bool *ch1, bool *ch2) {
    *ch1 = sim_gpio_ch1;
    *ch2 = sim_gpio_ch2;
}

/**
 * @brief Керування вихідним реле безпеки силового кола.
 */
static void Write_Safety_Relay(bool enable) {
    safety_relay_output = enable;
    printf("[RELAY] Силове реле безпеки: %s\n", enable ? "УВІМКНЕНО (ENABLE)" : "ВИМКНЕНО (SAFE STOP)");
}

int main(void) {
    printf("=== Запуск прошивки двоканального пристрою дозволу ===\n");

    // Конфігурація: антидребезг 10 мс, таймаут розсинхронізму 50 мс
    EnablingSwitchConfig_t switch_cfg = {
        .debounce_time_ms = 10,
        .discrepancy_time_ms = 50
    };

    EnablingSwitch_t enabling_switch;
    EnablingSwitch_Init(&enabling_switch, &switch_cfg);

    VigilanceTimer_t vigilance_timer;
    // Попередження через 3000 мс (3 сек), зупинка через 1000 мс (1 сек) для тесту
    VigilanceControl_Init(&vigilance_timer, 3000, 1000);

    const uint32_t system_tick_ms = 10; // Крок системного таймера

    // Тестовий сценарій 1: Початковий стан (Відпущено)
    printf("\n--- Сценарій 1: Початковий стан (Відпущено) ---\n");
    sim_gpio_ch1 = false;
    sim_gpio_ch2 = false;

    for (int step = 0; step < 3; ++step) {
        bool ch1, ch2;
        Read_HAL_GPIO(&ch1, &ch2);
        EnablingState_t state = EnablingSwitch_Update(&enabling_switch, ch1, ch2, system_tick_ms);
        VigilanceState_t vig = VigilanceControl_Update(&vigilance_timer, (state == ENABLING_STATE_ENABLED), system_tick_ms);

        Write_Safety_Relay(state == ENABLING_STATE_ENABLED && vig == VIGILANCE_OK);
    }

    // Тестовий сценарій 2: Синхронне натискання в Позицію 2 (Дозвіл)
    printf("\n--- Сценарій 2: Синхронне натискання в Позицію 2 (Дозвіл) ---\n");
    sim_gpio_ch1 = true;
    sim_gpio_ch2 = true;

    for (int step = 0; step < 5; ++step) {
        bool ch1, ch2;
        Read_HAL_GPIO(&ch1, &ch2);
        EnablingState_t state = EnablingSwitch_Update(&enabling_switch, ch1, ch2, system_tick_ms);
        VigilanceState_t vig = VigilanceControl_Update(&vigilance_timer, (state == ENABLING_STATE_ENABLED), system_tick_ms);

        Write_Safety_Relay(state == ENABLING_STATE_ENABLED && vig == VIGILANCE_OK);
    }

    // Тестовий сценарій 3: Симуляція короткого замикання / Розсинхронізму каналів
    printf("\n--- Сценарій 3: Симуляція короткого замикання / Розсинхронізму каналів ---\n");
    sim_gpio_ch1 = true;
    sim_gpio_ch2 = false; // Канал 2 обірвано

    for (int step = 0; step < 8; ++step) {
        bool ch1, ch2;
        Read_HAL_GPIO(&ch1, &ch2);
        EnablingState_t state = EnablingSwitch_Update(&enabling_switch, ch1, ch2, system_tick_ms);
        VigilanceState_t vig = VigilanceControl_Update(&vigilance_timer, (state == ENABLING_STATE_ENABLED), system_tick_ms);

        printf("Крок %d | Стан FSM: %d (0:REL, 1:ENA, 2:PAN, 3:FLT)\n", step, state);
        Write_Safety_Relay(state == ENABLING_STATE_ENABLED && vig == VIGILANCE_OK);
    }

    printf("\n=== Завершення тестування системи ===\n");
    return 0;
}
