#ifndef VERIFY_H
#define VERIFY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "boot_status.h"
#include "efuse.h"
#include "manifest.h"

/*
 * Готує крипторушій до роботи: віддає mbedTLS статичний пул пам'яті замість
 * купи. Викликати рівно один раз, до першої перевірки образу.
 */
void verify_init(void);

/*
 * Повний ланцюг перевірок образу — п'ять кроків, кожен зупиняє процес:
 *   1) заголовок уже розібрано (magic + CRC-32) у manifest_parse();
 *   2) біт відкликання слота в eFuse;
 *   3) звірка хешу відкритого ключа з еталоном Root of Trust;
 *   4) монотонний лічильник анти-відкату;
 *   5) математична перевірка підпису над заголовком і тілом.
 */
boot_status_t boot_verify_image(const firmware_manifest_t *manifest,
                                const uint8_t *payload,
                                const efuse_mirror_t *efuse);

/*
 * Побайтове порівняння за сталий час. Завжди проходить усі size байтів,
 * накопичуючи різницю через XOR: час виконання не залежить від того,
 * на якій позиції виникла розбіжність.
 */
bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t size);

#endif /* VERIFY_H */
