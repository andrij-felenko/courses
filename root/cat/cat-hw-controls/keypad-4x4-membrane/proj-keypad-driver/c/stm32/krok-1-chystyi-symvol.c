#include "stm32f4xx_hal.h"
#include <stdio.h>

#define ROWS 4
#define COLS 4

// що НАДРУКОВАНО на клавіатурі, [рядок][стовпець]:
const char keys[ROWS][COLS] = {
    {'1','2','3','A'},
    {'4','5','6','B'},
    {'7','8','9','C'},
    {'*','0','#','D'}
};
const uint16_t row_pins[ROWS] = {GPIO_PIN_0, GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3};
const uint16_t col_pins[COLS] = {GPIO_PIN_4, GPIO_PIN_5, GPIO_PIN_6, GPIO_PIN_7};

// Стовпець або веде «0», або відпущений у високий опір («Z»).
// Двох ведених ліній одночасно бути не мусить — інакше натиск замкне вихід на вихід.
void col_drive(uint16_t pin, int active) {
    GPIO_InitTypeDef g = {0};
    g.Pin   = pin;
    g.Mode  = active ? GPIO_MODE_OUTPUT_PP : GPIO_MODE_INPUT;
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &g);
    if (active) HAL_GPIO_WritePin(GPIOB, pin, GPIO_PIN_RESET);
}

void keypad_init(void) {
    __HAL_RCC_GPIOB_CLK_ENABLE();
    GPIO_InitTypeDef g = {0};
    g.Pin  = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3;
    g.Mode = GPIO_MODE_INPUT;
    g.Pull = GPIO_PULLUP;                       // рядки у спокої «1»
    HAL_GPIO_Init(GPIOB, &g);
    for (int c = 0; c < COLS; c++) col_drive(col_pins[c], 0);
}

// один прохід сітки: 0 — нічого не натиснуто, інакше символ
char keypad_scan(void) {
    for (int c = 0; c < COLS; c++) {
        col_drive(col_pins[c], 1);                       // ведемо РІВНО один стовпець
        for (volatile int d = 0; d < 200; d++) { }       // дати рівню осісти
        char found = 0;
        for (int r = 0; r < ROWS; r++)
            if (HAL_GPIO_ReadPin(GPIOB, row_pins[r]) == GPIO_PIN_RESET) {
                found = keys[r][c]; break;
            }
        col_drive(col_pins[c], 0);                       // відпустили у «Z»
        if (found) return found;
    }
    return 0;
}

int main(void) {
    HAL_Init();
    SystemClock_Config();          // готує CubeMX
    keypad_init();
    char prev = 0;
    while (1) {
        char k = keypad_scan();
        if (k && k != prev) printf("клавіша: %c\n", k);  // край, а не рівень
        prev = k;
        HAL_Delay(20);             // 20 мс — і антидеренч, і крок циклу
    }
}
