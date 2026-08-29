#include "dfu_proto.h"

/* bmAttributes = 0x0B: пишемо (bit0), читаємо (bit1), самі від'єднуємось (bit3).
   bitManifestationTolerant = 0 — після фіналізації образу потрібен перезапуск. */
const dfu_functional_descriptor_t dfu_functional_descriptor = {
    .bLength         = sizeof(dfu_functional_descriptor_t),
    .bDescriptorType = DFU_FUNC_DESC_TYPE,
    .bmAttributes    = 0x0Bu,
    .wDetachTimeOut  = 250u,
    .wTransferSize   = (uint16_t)DFU_TRANSFER_SIZE,
    .bcdDFUVersion   = 0x0110u
};

uint32_t dfu_le32(const uint8_t *p)
{
    return (uint32_t)p[0]
         | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16)
         | ((uint32_t)p[3] << 24);
}

void dfu_pack_status(const dfu_status_report_t *report, uint8_t out[DFU_GETSTATUS_LEN])
{
    uint32_t poll = report->poll_timeout_ms;

    /* Поле bwPollTimeout 24-бітне: більше 16777 секунд не пообіцяєш. */
    if (poll > 0x00FFFFFFu) {
        poll = 0x00FFFFFFu;
    }

    out[0] = (uint8_t)report->status;
    out[1] = (uint8_t)(poll & 0xFFu);
    out[2] = (uint8_t)((poll >> 8) & 0xFFu);
    out[3] = (uint8_t)((poll >> 16) & 0xFFu);
    out[4] = (uint8_t)report->state;
    out[5] = report->string_index;
}

dfu_status_t dfuse_parse_command(const uint8_t *payload, size_t len, dfuse_command_t *out)
{
    if (payload == NULL || out == NULL || len == 0u) {
        return DFU_ERR_STALLEDPKT;
    }

    out->address = 0u;
    out->mass_erase = 0u;

    switch (payload[0]) {
    case DFUSE_SET_ADDRESS:
        /* Один байт команди + 4 байти адреси, більше нічого бути не може. */
        if (len != 5u) {
            return DFU_ERR_STALLEDPKT;
        }
        out->kind = DFUSE_SET_ADDRESS;
        out->address = dfu_le32(&payload[1]);
        /* Далі програмуємо словами, тож невирівняну адресу відхиляємо одразу. */
        if ((out->address & 3u) != 0u) {
            return DFU_ERR_ADDRESS;
        }
        return DFU_OK;

    case DFUSE_ERASE:
        out->kind = DFUSE_ERASE;
        if (len == 1u) {
            out->mass_erase = 1u; /* Стирання всієї області застосунку */
            return DFU_OK;
        }
        if (len != 5u) {
            return DFU_ERR_STALLEDPKT;
        }
        out->address = dfu_le32(&payload[1]);
        return DFU_OK;

    case DFUSE_READ_UNPROTECT:
        /* Зняття RDP стирає весь кристал разом із калібруванням і самим
           завантажувачем — свідомо не підтримуємо. */
        return DFU_ERR_VENDOR;

    default:
        return DFU_ERR_VENDOR;
    }
}
