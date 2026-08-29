#include <string.h>

#include "crc32.h"
#include "manifest.h"

boot_status_t manifest_parse(const uint8_t *slot_base,
                             uint32_t slot_size,
                             firmware_manifest_t *out)
{
    if (slot_base == NULL || out == NULL || slot_size < MANIFEST_SIZE) {
        return BOOT_ERR_FLASH_READ;
    }

    /*
     * Копіюємо заголовок у SRAM одним memcpy і далі працюємо тільки з копією.
     * Причина не в стилі: Flash під час перевірки може бути перезаписаний
     * зовнішнім агентом (DMA контролера оновлення), і тоді перевірене поле
     * і використане поле — різні значення. Копія вбиває цю гонку.
     */
    memcpy(out, slot_base, MANIFEST_SIZE);

    if (out->magic != MANIFEST_MAGIC) {
        return BOOT_ERR_MAGIC;
    }

    /* CRC-32 накриває все, що йде після самого поля CRC. */
    const uint8_t *header = (const uint8_t *)out;
    uint32_t computed = crc32_ieee(header + MANIFEST_CRC_OFFSET,
                                   MANIFEST_SIZE - MANIFEST_CRC_OFFSET);
    if (computed != out->header_crc) {
        return BOOT_ERR_MAGIC;
    }

    if (out->key_slot_index >= BOOT_KEY_SLOTS) {
        return BOOT_ERR_INVALID_SLOT;
    }

    if (out->reserved[0] != 0 || out->reserved[1] != 0 || out->reserved[2] != 0) {
        /* Резерв — це майбутні прапорці; невідоме значення читати не вміємо. */
        return BOOT_ERR_MAGIC;
    }

    if (out->payload_length == 0U ||
        out->payload_length > slot_size - (uint32_t)MANIFEST_SIZE) {
        return BOOT_ERR_FLASH_READ;
    }

    return BOOT_OK;
}
