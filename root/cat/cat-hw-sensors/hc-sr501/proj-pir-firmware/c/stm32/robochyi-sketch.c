#include "main.h"        // CubeMX: PIR_Pin — вхід NOPULL, RELAY_Pin — вихід push-pull

#define WARMUP_MS    60000U   // прогрів: перша хвилина — не вірити
#define DEBOUNCE_MS  40U      // скільки тримати рівень, щоб повірити
#define HOLD_MS      5000U    // власний "хвіст" після зникнення руху

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    HAL_GPIO_WritePin(RELAY_GPIO_Port, RELAY_Pin, GPIO_PIN_RESET);   // світло вимкнене

    uint32_t t_boot = HAL_GetTick(), t_edge = t_boot, t_last_motion = 0;
    GPIO_PinState raw_prev = HAL_GPIO_ReadPin(PIR_GPIO_Port, PIR_Pin);
    GPIO_PinState stable   = GPIO_PIN_RESET;
    uint8_t light_on = 0;

    while (1) {
        HAL_Delay(5);                     // крок циклу
        uint32_t now = HAL_GetTick();     // лічильник мілісекунд від SysTick

        // --- Шар 1: гасіння прогріву. Першу хвилину виходу не віримо. ---
        if (now - t_boot < WARMUP_MS) {
            HAL_GPIO_WritePin(RELAY_GPIO_Port, RELAY_Pin, GPIO_PIN_RESET);
            continue;
        }

        // --- Шар 2: дебаунс. Рівень мусить протриматися DEBOUNCE_MS. ---
        GPIO_PinState raw = HAL_GPIO_ReadPin(PIR_GPIO_Port, PIR_Pin);
        if (raw != raw_prev) { t_edge = now; raw_prev = raw; }
        if (now - t_edge >= DEBOUNCE_MS) stable = raw;
        if (stable == GPIO_PIN_SET) t_last_motion = now;

        // --- Шар 3: рішення про світло з власним "хвостом" HOLD_MS. ---
        uint8_t want_on = (now - t_last_motion < HOLD_MS) ? 1 : 0;
        if (want_on != light_on) {
            light_on = want_on;
            HAL_GPIO_WritePin(RELAY_GPIO_Port, RELAY_Pin,
                              light_on ? GPIO_PIN_SET : GPIO_PIN_RESET);
        }
    }
}
