#include "flash_budget.h"

#include <string.h>

/* Золоте правило статті: образ не більший за 45 % повного Flash. */
#define FLASH_IMAGE_LIMIT_PM 450u

budget_flags_t flash_budget_audit(const flash_layout_t *layout,
                                  flash_report_t *report)
{
    if (report != NULL) {
        memset(report, 0, sizeof *report);
    }
    if (layout == NULL || layout->total_bytes == 0u ||
        layout->sector_bytes == 0u) {
        return BUDGET_FLASH_NO_OTA;
    }

    uint32_t overhead = layout->bootloader_bytes + layout->nvs_bytes;
    if (overhead >= layout->total_bytes) {
        return BUDGET_FLASH_NO_OTA;
    }

    uint32_t for_slots = layout->total_bytes - overhead;

    /* Слот мусить бути кратним сектору стирання, інакше стирання зачепить сусіда. */
    uint32_t slot = (for_slots / 2u) / layout->sector_bytes * layout->sector_bytes;

    budget_flags_t flags = BUDGET_OK;
    if (slot == 0u || layout->image_bytes > slot) {
        flags |= BUDGET_FLASH_NO_OTA;
    }

    uint32_t share_pm =
        (uint32_t)((uint64_t)layout->image_bytes * 1000u / layout->total_bytes);
    if (share_pm > FLASH_IMAGE_LIMIT_PM) {
        flags |= BUDGET_FLASH_TIGHT;
    }

    if (report != NULL) {
        report->slot_bytes      = slot;
        report->slot_free_bytes = (layout->image_bytes < slot)
                                      ? slot - layout->image_bytes
                                      : 0u;
        report->image_share_pm  = share_pm;
        report->unusable_bytes  = for_slots - slot * 2u;
        report->dual_bank_ready = (flags & BUDGET_FLASH_NO_OTA) == 0u;
    }

    return flags;
}
