/* sf_flash.h — контракт носія для черги.
 *
 * Черга нічого не знає ні про SPI, ні про модель мікросхеми. Їй потрібні
 * три дії й два числа, і саме на цій межі проходить розділ між «як воно
 * влаштоване» і «як ним користуються».
 *
 * Правила NOR, які контракт НЕ ховає, бо на них тримається вся черга:
 *  - програмування вміє лише гасити біти (1 -> 0); підняти біт назад
 *    може тільки стирання цілого сектора;
 *  - стертий сектор — суцільні 0xFF;
 *  - дозапис у стерту область не потребує стирання, тому черга й
 *    працює як журнал append-only.
 */
#ifndef SF_FLASH_H
#define SF_FLASH_H

#include <stdint.h>

typedef enum {
    SF_FLASH_OK = 0,
    SF_FLASH_EIO,     /* шина не відповіла або мікросхема відкинула команду */
    SF_FLASH_ETIME,   /* операція не завершилась за паспортний час          */
    SF_FLASH_EPARAM,  /* адреса поза межами кристала                        */
} sf_flash_err_t;

typedef struct {
    sf_flash_err_t (*read)(void *ctx, uint32_t addr, void *dst, uint32_t len);
    sf_flash_err_t (*program)(void *ctx, uint32_t addr, const void *src, uint32_t len);
    sf_flash_err_t (*erase_sector)(void *ctx, uint32_t addr);

    void    *ctx;
    uint32_t sector_size; /* найменша одиниця стирання, зазвичай 4096 */
    uint32_t page_size;   /* найбільший неподільний запис, зазвичай 256 */
    uint32_t capacity;    /* повний обсяг кристала в байтах */
} sf_flash_dev_t;

#endif /* SF_FLASH_H */
