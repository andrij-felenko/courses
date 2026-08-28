#include "driver/gpio.h"

// Ті самі шість ліній; вивід МК тут називається номером GPIO.
#define LCD_RS  GPIO_NUM_18       // RS → GPIO18
#define LCD_E   GPIO_NUM_19       // E  → GPIO19
#define LCD_D4  GPIO_NUM_21
#define LCD_D5  GPIO_NUM_22
#define LCD_D6  GPIO_NUM_23
#define LCD_D7  GPIO_NUM_25

// Готового «LiquidCrystal» в ESP-IDF немає — карту ліній даних тримаємо самі.
// Порядок у цьому масиві такий самий критичний, як порядок аргументів конструктора.
static const gpio_num_t LCD_DATA[4] = { LCD_D4, LCD_D5, LCD_D6, LCD_D7 };
