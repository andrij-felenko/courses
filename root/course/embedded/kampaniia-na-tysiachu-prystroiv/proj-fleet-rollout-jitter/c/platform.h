/* Апаратні гачки вузла парку.
 *
 * На реальному MCU кожну з цих функцій реалізує HAL конкретного сімейства:
 * RTC Backup Domain, блок TRNG, контролер Flash. Поруч лежить platform_sim.c —
 * реалізація для хоста, щоб усю кампанію можна було прогнати цілком і побачити,
 * як стан переживає перезавантаження. */
#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Регістри RTC Backup Domain: переживають скидання ядра й сторожовий таймер,
 * але не зникнення живлення (STM32F4 — 20 слів, F7 — 32). */
#define PLAT_BKP_WORDS 32u

uint32_t plat_bkp_read(unsigned idx);
void     plat_bkp_write(unsigned idx, uint32_t value);

/* Джерела апаратної ентропії. Кожне може бути відсутнє на конкретній платі —
 * тоді функція повертає 0, а сівба змішує те, що лишилося (див. jitter.c). */
uint32_t plat_trng_word(void);        /* апаратний генератор                    */
uint32_t plat_adc_noise_word(void);   /* молодші біти непідключеного входу АЦП   */
uint32_t plat_timer_jitter_word(void);/* мікросекундні коливання між перериваннями */

uint64_t plat_uptime_ms(void);
void     plat_delay_ms(uint32_t ms);

/* Геометрія Flash. Стирання — сторінкою, запис — квантом у 8 байтів
 * (подвійне слово STM32L4/G4); одна й та сама комірка не переписується двічі. */
#define PLAT_FLASH_BASE 0x08000000u
#define PLAT_FLASH_SIZE (1024u * 1024u)
#define PLAT_FLASH_PAGE 2048u
#define PLAT_FLASH_WORD 8u

bool plat_flash_unlock(void);
void plat_flash_lock(void);
bool plat_flash_erase_page(uint32_t addr);
bool plat_flash_program(uint32_t addr, const uint8_t *data, size_t len);

/* Flash відображена в адресний простір — читання йде звичайним покажчиком. */
const uint8_t *plat_flash_ptr(uint32_t addr);

/* Унікальний ідентифікатор чипа (STM32 — 96 біт за 0x1FFF7A10, доповнені нулями). */
void plat_hardware_id(uint8_t out[16]);

/* NVIC_SystemReset(). У симуляції — піднімає прапорець, який знімає main.c. */
void plat_reboot(void);

/* Лише для хостової симуляції: чи запитано перезавантаження. */
bool plat_sim_take_reboot(void);

#endif /* PLATFORM_H */
