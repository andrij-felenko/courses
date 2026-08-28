#include "stm32f1xx_hal.h"        // або заголовок своєї серії

// Вивід тут — пара «порт + пін»; у CubeMX усі шість позначені GPIO_Output.
#define LCD_RS_PORT  GPIOB
#define LCD_RS_PIN   GPIO_PIN_0   // RS
#define LCD_E_PORT   GPIOB
#define LCD_E_PIN    GPIO_PIN_1   // E

// Чотири лінії даних — таблицею, у порядку D4, D5, D6, D7.
static GPIO_TypeDef *const LCD_D_PORT[4] = { GPIOB, GPIOB, GPIOB, GPIOB };
static const uint16_t      LCD_D_PIN[4]  = { GPIO_PIN_4, GPIO_PIN_5,
                                             GPIO_PIN_6, GPIO_PIN_7 };
