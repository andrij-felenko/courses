/* license_table.h — таблиця атрибуції, прошита у Flash разом із кодом.
 *
 * Таблиця статична й незмінна: усі рядки лежать у .rodata, у SRAM не потрапляє
 * жоден байт. Це принципово для приладу з 128 КБ оперативної пам'яті, де копія
 * такого тексту з'їла б відсоток бюджету заради даних, які ніколи не міняються.
 */
#ifndef LICENSE_TABLE_H
#define LICENSE_TABLE_H

#include <stddef.h>

typedef struct {
    const char *name;      /* назва компонента, ASCII — рівно як у SBOM */
    const char *version;   /* версія, що потрапила в цю збірку           */
    const char *spdx;      /* ідентифікатор або вираз SPDX               */
    const char *holder;    /* правовласник                              */
    const char *notice;    /* обов'язкове застереження або NULL          */
} license_entry_t;

/* Виріб і збірка. FW_SBOM_SHA256 підставляє конвеєр:
 *     -DFW_SBOM_SHA256=\"$(sha256sum build/firmware.cdx.json | cut -c1-64)\"
 * так консольна відповідь пристрою прив'язується до підписаного паспорта. */
extern const char *const fw_product_name;
extern const char *const fw_product_version;
extern const char *const fw_sbom_sha256;

extern const license_entry_t license_table[];
extern const size_t license_table_count;

/* Пошук за початком назви, без урахування регістру. NULL — не знайдено. */
const license_entry_t *license_table_find(const char *prefix);

#endif /* LICENSE_TABLE_H */
