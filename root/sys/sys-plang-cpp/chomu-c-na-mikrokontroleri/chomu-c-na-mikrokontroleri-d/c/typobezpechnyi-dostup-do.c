/* Доступ до регістрів мовою C через макроси CMSIS */
#include <stdint.h>

#define GPIOA_BASE  0x40020000UL
#define GPIOA_MODER (*(volatile uint32_t*)(GPIOA_BASE + 0x00))
#define GPIOA_IDR   (*(volatile uint32_t*)(GPIOA_BASE + 0x10))

/* Помилка: випадковий запис у регістр тільки для читання (IDR) */
void bad_c_code(void) {
    GPIOA_IDR = 0x1234; /* Компілятор C не бачить помилки! */
}
