#include <stdint.h>
#include "cmsis_compiler.h"

/* Атомарний інкремент без вимкнення переривань на чистій апаратурі */
uint32_t atomic_fetch_add_arm(volatile uint32_t *ptr, uint32_t value) {
    uint32_t old_val;
    uint32_t status;
    
    do {
        old_val = __LDREXW((volatile uint32_t *)ptr); // Читаємо та зводимо монітор
        status = __STREXW(old_val + value, (volatile uint32_t *)ptr); // Спроба запису
    } while (status != 0U); // Повторюємо, якщо статус 1 (було переривання)
    
    return old_val;
}
