/* sf_flash_sim.h — модель NOR у ОЗП.
 *
 * Потрібна не «щоб потестувати», а щоб показати те, чого на живому
 * пристрої не покажеш на занятті: знеструмлення посеред програмування
 * сторінки. Модель тримає справжню семантику NOR — програмування лише
 * гасить біти (dst &= src), стирання піднімає сектор у 0xFF, — тож
 * обірваний запис лишає по собі рівно те саме сміття, що й у кристалі.
 *
 * Пам'ять дає викликач (статичний масив): жодного malloc.
 */
#ifndef SF_FLASH_SIM_H
#define SF_FLASH_SIM_H

#include <stdbool.h>
#include <stdint.h>

#include "sf_flash.h"

#define SF_SIM_UNLIMITED 0xFFFFFFFFu

typedef struct {
    uint8_t *mem;
    uint32_t capacity;
    uint32_t sector_size;
    uint32_t page_size;

    /* Скільки байтів іще дозволено запрограмувати до «зникнення живлення».
     * Дійшовши до нуля, program допише скільки встиг і поверне EIO. */
    uint32_t write_budget;
    bool     powered;

    uint32_t erase_count;
    uint32_t program_count;
} sf_flash_sim_t;

void sf_flash_sim_init(sf_flash_sim_t *sim, uint8_t *storage, uint32_t capacity,
                       uint32_t sector_size, uint32_t page_size, sf_flash_dev_t *dev);

/* Стерти весь кристал — стан «з магазину». */
void sf_flash_sim_bulk_erase(sf_flash_sim_t *sim);

/* Зрізати живлення після наступних n запрограмованих байтів. */
void sf_flash_sim_cut_power_after(sf_flash_sim_t *sim, uint32_t n);

/* Подати живлення знову: вміст пам'яті лишається таким, яким його
 * застало зникнення напруги. */
void sf_flash_sim_power_up(sf_flash_sim_t *sim);

#endif /* SF_FLASH_SIM_H */
