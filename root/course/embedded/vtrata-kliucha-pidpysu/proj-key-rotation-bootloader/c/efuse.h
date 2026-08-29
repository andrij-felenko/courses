#ifndef EFUSE_H
#define EFUSE_H

#include <stdbool.h>
#include <stdint.h>

#include "boot_status.h"
#include "manifest.h"

/* Біти відкликання: рядок EFUSE_ROW_REVOKE, по одному біту на слот ключа. */
#define REVOKE_KEY0  (1U << 0)
#define REVOKE_KEY1  (1U << 1)
#define REVOKE_KEY2  (1U << 2)
#define REVOKE_KEY3  (1U << 3)

/* Лічильник анти-відкату закодовано термометром: значення = кількість спалених бітів. */
#define EFUSE_COUNTER_BITS  32U

/*
 * Тіньова копія eFuse у SRAM. Читаємо її один раз на старті: кожне звертання
 * до контролера перемичок коштує десятки тактів, а ланцюг перевірок торкається
 * тих самих полів багато разів.
 */
typedef struct {
    uint8_t  root_key_digest[BOOT_KEY_SLOTS][SHA256_SIZE];
    uint8_t  revocation_bits;    /* маска REVOKE_KEYn */
    uint32_t monotonic_counter;  /* уже розкодоване значення термометра */
} efuse_mirror_t;

/* Зчитує весь потрібний завантажувачу вміст перемичок у тіньову копію. */
boot_status_t efuse_read_mirror(efuse_mirror_t *out);

/*
 * Незворотно палить біт відкликання слота. Перед імпульсом перевіряє детектор
 * просідання напруги, після імпульсу — контрольне зчитування у звичайному
 * і в граничному (Marginal Read) режимах.
 */
boot_status_t efuse_burn_revocation(uint8_t slot_index);

/* Піднімає апаратний лічильник до version, допалюючи бракуючі біти термометра. */
boot_status_t efuse_burn_counter(uint32_t version);

#endif /* EFUSE_H */
