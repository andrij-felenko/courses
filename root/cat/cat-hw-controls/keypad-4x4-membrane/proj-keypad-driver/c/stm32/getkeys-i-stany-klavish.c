#include "stm32f4xx_hal.h"
#include <stdio.h>

// keys / row_pins / col_pins / col_drive() / keypad_init() — з вкладки STM32 кроку 1.
extern const char keys[4][4];
extern const uint16_t row_pins[4], col_pins[4];
void col_drive(uint16_t pin, int active);
void keypad_init(void);

typedef enum { KEY_IDLE, KEY_PRESSED, KEY_HOLD } key_state_t;

#define DEBOUNCE_MS   20
#define HOLD_MS     1000     // "тримають" = утримання понад 1000 мс

static key_state_t st[4][4];        // маленький автомат на КОЖНУ клавішу
static uint32_t    t_st[4][4];      // коли стан цієї клавіші востаннє змінився

// Один прохід сітки. Ведений стовпець читає ВСІ чотири рядки, тож кілька
// одночасних клавіш видно самі собою — окремої "getKeys" тут не треба.
// Друкуємо лише на ЗМІНУ стану: рівень сам по собі події не дає.
void keypad_poll(void) {
    uint32_t now = HAL_GetTick();
    for (int c = 0; c < 4; c++) {
        col_drive(col_pins[c], 1);
        for (volatile int d = 0; d < 200; d++) { }
        for (int r = 0; r < 4; r++) {
            int down = (HAL_GPIO_ReadPin(GPIOB, row_pins[r]) == GPIO_PIN_RESET);
            uint32_t age = now - t_st[r][c];        // скільки стан уже тримається
            if (down && st[r][c] == KEY_IDLE && age >= DEBOUNCE_MS) {
                st[r][c] = KEY_PRESSED; t_st[r][c] = now;
                printf("натиснуто: %c\n", keys[r][c]);
            } else if (down && st[r][c] == KEY_PRESSED && age >= HOLD_MS) {
                st[r][c] = KEY_HOLD; t_st[r][c] = now;
                printf("довге утримання: %c\n", keys[r][c]);
            } else if (!down && st[r][c] != KEY_IDLE && age >= DEBOUNCE_MS) {
                st[r][c] = KEY_IDLE; t_st[r][c] = now;
                printf("відпущено: %c\n", keys[r][c]);
            }
        }
        col_drive(col_pins[c], 0);
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    keypad_init();
    while (1) {
        keypad_poll();
        HAL_Delay(5);
    }
}
