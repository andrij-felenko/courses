/* chip_regops.h — Рівень 2: безпечна робота з регістрами й тіньовим станом.
 *
 * Прямий Read-Modify-Write по шині заборонено: він скидає прапорці регістрів
 * clear-on-read, псує регістри лише для запису й затирає заводські біти
 * калібрування. Замість читання з чипа драйвер бере поточне значення з
 * тіньової копії в ОЗП і оновлює її лише після підтвердженого запису.
 */
#ifndef CHIP_REGOPS_H
#define CHIP_REGOPS_H

#include <stdint.h>

#include "chip_dev.h"
#include "chip_status.h"

/* Тіньова комірка для конфігураційного регістру; NULL — регістр не тіньовий
 * (наприклад STATUS чи OUT_*, які читаються з чипа щоразу). */
uint8_t *chip_reg_shadow(chip_dev_t *dev, uint8_t reg);

/* Записати регістр «як є» і синхронно оновити тінь. */
chip_status_t chip_reg_write(chip_dev_t *dev, uint8_t reg, uint8_t value);

/* Оновити одне бітове поле: значення береться з тіні, поле обнуляється
 * інвертованою маскою, нове значення зсувається на позицію поля. */
chip_status_t chip_reg_update_field(chip_dev_t *dev, uint8_t reg,
                                    uint8_t mask, uint8_t shift, uint8_t value);

/* Виставити/зняти окремі біти тіньового регістру. */
chip_status_t chip_reg_set_bits(chip_dev_t *dev, uint8_t reg, uint8_t bits);
chip_status_t chip_reg_clear_bits(chip_dev_t *dev, uint8_t reg, uint8_t bits);

/* Пакетне зчитування суміжних регістрів однією транзакцією з автоінкрементом
 * адреси — атомарний знімок блоку даних, а не шість окремих команд. */
chip_status_t chip_reg_read_burst(chip_dev_t *dev, uint8_t start_reg,
                                  uint8_t *buf, uint16_t len);

/* Прочитати з чипа справжній вміст читабельних конфігураційних регістрів і
 * покласти його в тінь. Викликається один раз при ініціалізації, щоб тінь
 * стартувала не з нуля, а з того, що насправді лежить у кремнії. */
chip_status_t chip_reg_sync_shadow(chip_dev_t *dev);

#endif /* CHIP_REGOPS_H */
