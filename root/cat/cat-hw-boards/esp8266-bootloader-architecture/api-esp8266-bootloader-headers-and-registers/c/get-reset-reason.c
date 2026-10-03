#include <stdint.h>

#define RTC_STORE0_REG  (*(volatile uint32_t *)(0x60001200))
#define RTC_STATE_REG   (*(volatile uint32_t *)(0x60000b00))

/* Зчитування коду причини скидання */
uint8_t get_reset_reason(void) {
    /* Отримання коду з молодших 4 бітів регістра стану */
    return (uint8_t)(RTC_STATE_REG & 0x0F);
}

/* Запис вектора швидкого перезапуску в RTC_STORE0 */
void set_fast_boot_vector(uint32_t entry_point) {
    RTC_STORE0_REG = entry_point;
}
