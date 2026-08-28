// Той самий автоповтор на STM32 HAL: мілісекунди дає HAL_GetTick(), розбір NEC — з кроку 2
#include "main.h"

#define MY_REMOTE  0x00
#define REPEAT_MS  120                  // ВЛАСНИЙ темп автоповтору, мс
#define RELEASE_MS 250                  // тиша довша за це = кнопку відпустили
enum { BTN_UP = 0x15, BTN_DOWN = 0x07 };

static uint8_t  brightness   = 128;
static uint16_t held_command = 0;       // яку кнопку тримають (0 = жодну)

// одна «дія кнопки» — крок регулювання
static void step_button(uint16_t cmd) {
    if (cmd == BTN_UP   && brightness <= 250) brightness += 5;
    if (cmd == BTN_DOWN && brightness >= 5)   brightness -= 5;
    apply_brightness();
}

int main(void) {
    HAL_Init(); SystemClock_Config();
    MX_GPIO_Init(); MX_TIM2_Init(); MX_TIM3_Init();
    HAL_TIM_Base_Start(&htim2);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    uint32_t last_action = 0, last_frame = 0;

    while (1) {
        // 1) прийшов кадр (перший чи повтор) — відзначаємо, що кнопку ще тримають
        if (rx_ready) {
            uint16_t cmd = rx_cmd;
            uint8_t  repeat = rx_repeat, mine = (rx_addr == MY_REMOTE);
            rx_ready = 0;               // звільнили приймач під наступний кадр
            if (mine) {
                last_frame = HAL_GetTick();   // будь-який наш кадр = «кнопка ще жива»
                if (!repeat) {          // новий натиск: діємо одразу й беремо «на утримання»
                    held_command = cmd;
                    step_button(cmd);
                    last_action = HAL_GetTick();
                }
            }
        }

        // 2) поки кнопку тримають — крутимо значення СВОЇМ темпом
        if (held_command && HAL_GetTick() - last_action >= REPEAT_MS) {
            step_button(held_command);
            last_action = HAL_GetTick();
        }

        // 3) якщо кадрів/повторів давно нема — кнопку відпустили
        if (held_command && HAL_GetTick() - last_frame > RELEASE_MS) held_command = 0;
    }
}
