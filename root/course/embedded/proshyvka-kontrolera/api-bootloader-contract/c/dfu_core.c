#include <string.h>

#include "boot_trigger.h"
#include "dfu_core.h"
#include "flash_map.h"

/* Скільки чекати хостові після звичайного запису блоку. */
#define DFU_WRITE_POLL_MS 5u
/* Фіналізація: перевірка образу перед перезапуском. */
#define DFU_MANIFEST_POLL_MS 500u

/* Відповідь на DFU_UPLOAD із wBlockNum = 0 — перелік підтриманих команд DfuSe. */
static const uint8_t dfuse_supported_commands[] = {
    0x00u,               /* Get Commands */
    DFUSE_SET_ADDRESS,
    DFUSE_ERASE
};

void dfu_init(dfu_device_t *dev)
{
    memset(dev, 0, sizeof *dev);
    dev->state = DFU_STATE_IDLE;   /* завантажувач стартує вже в dfuIDLE */
    dev->status = DFU_OK;
    dev->address_pointer = FLASH_BASE_ADDR; /* типова точка ST DfuSe */
    dev->op = DFU_OP_NONE;
    dev->poll_timeout_ms = DFU_WRITE_POLL_MS;
}

static int fail(dfu_device_t *dev, dfu_status_t status)
{
    dev->status = status;
    dev->state = DFU_STATE_ERROR;
    dev->op = DFU_OP_NONE;
    return -1;
}

static int handle_dnload(dfu_device_t *dev, uint16_t block_num,
                         const uint8_t *data, size_t data_len)
{
    if (dev->state != DFU_STATE_IDLE && dev->state != DFU_STATE_DNLOAD_IDLE) {
        return fail(dev, DFU_ERR_STALLEDPKT);
    }

    /* Блок нульової довжини = кінець образу, переходимо до фіналізації. */
    if (data_len == 0u) {
        dev->op = DFU_OP_MANIFEST;
        dev->poll_timeout_ms = DFU_MANIFEST_POLL_MS;
        dev->state = DFU_STATE_MANIFEST_SYNC;
        return 0;
    }

    if (block_num == 0u) {
        dfuse_command_t cmd;
        dfu_status_t status = dfuse_parse_command(data, data_len, &cmd);
        if (status != DFU_OK) {
            return fail(dev, status);
        }

        if (cmd.kind == DFUSE_SET_ADDRESS) {
            /* Саму адресу перевіряємо тут, а не при записі: хост має дізнатись
               про промах одразу з першого ж GETSTATUS. */
            if (flash_map_sector_at(cmd.address) == NULL) {
                return fail(dev, DFU_ERR_ADDRESS);
            }
            dev->address_pointer = cmd.address;
            dev->op = DFU_OP_NONE;
            dev->poll_timeout_ms = 0u;
        } else { /* DFUSE_ERASE */
            if (cmd.mass_erase != 0u) {
                dev->op = DFU_OP_ERASE_APP;
                dev->poll_timeout_ms = flash_map_app_erase_timeout_ms();
            } else {
                const flash_sector_t *sector = flash_map_sector_at(cmd.address);
                if (sector == NULL) {
                    return fail(dev, DFU_ERR_ADDRESS);
                }
                dev->op = DFU_OP_ERASE;
                dev->op_address = sector->address;
                dev->poll_timeout_ms = flash_map_erase_timeout_ms(sector);
            }
        }

        dev->state = DFU_STATE_DNLOAD_SYNC;
        return 0;
    }

    if (block_num == 1u) {
        /* Номер 1 зарезервовано специфікацією DfuSe і не використовується. */
        return fail(dev, DFU_ERR_STALLEDPKT);
    }

    if (data_len > DFU_TRANSFER_SIZE) {
        return fail(dev, DFU_ERR_STALLEDPKT);
    }

    /* Адреса блоку рахується від покажчика: перший блок даних має номер 2. */
    dev->op_address = dev->address_pointer +
                      ((uint32_t)block_num - 2u) * DFU_TRANSFER_SIZE;
    if (!flash_map_is_app_range(dev->op_address, data_len)) {
        return fail(dev, DFU_ERR_ADDRESS);
    }

    memcpy(dev->buffer, data, data_len);
    dev->op_length = data_len;
    dev->op = DFU_OP_WRITE;
    dev->poll_timeout_ms = DFU_WRITE_POLL_MS;
    dev->state = DFU_STATE_DNLOAD_SYNC;
    return 0;
}

static int handle_upload(dfu_device_t *dev, uint16_t block_num, uint16_t length,
                         const uint8_t **out, size_t *out_len)
{
    if (dev->state != DFU_STATE_IDLE && dev->state != DFU_STATE_UPLOAD_IDLE) {
        return fail(dev, DFU_ERR_STALLEDPKT);
    }

    if (block_num == 0u) {
        *out = dfuse_supported_commands;
        *out_len = sizeof dfuse_supported_commands;
        dev->state = DFU_STATE_IDLE;
        return 0;
    }

    if (block_num == 1u || length == 0u) {
        return fail(dev, DFU_ERR_STALLEDPKT);
    }

    {
        uint32_t address = dev->address_pointer +
                           ((uint32_t)block_num - 2u) * DFU_TRANSFER_SIZE;
        size_t want = (length > DFU_TRANSFER_SIZE) ? DFU_TRANSFER_SIZE : length;
        const uint8_t *src = flash_read(address, want);

        if (src == NULL) {
            return fail(dev, DFU_ERR_ADDRESS);
        }
        *out = src;
        *out_len = want;
    }

    dev->state = DFU_STATE_UPLOAD_IDLE;
    return 0;
}

static int handle_getstatus(dfu_device_t *dev, const uint8_t **out, size_t *out_len)
{
    dfu_status_report_t report;

    report.status = dev->status;
    report.poll_timeout_ms = 0u;
    report.state = dev->state;
    report.string_index = 0u;

    if (dev->state == DFU_STATE_DNLOAD_SYNC) {
        if (dev->op == DFU_OP_NONE) {
            /* Set Address Pointer нічого не пише — синхронізація миттєва. */
            dev->state = DFU_STATE_DNLOAD_IDLE;
            report.state = DFU_STATE_DNLOAD_IDLE;
        } else {
            dev->state = DFU_STATE_DNBUSY;
            report.state = DFU_STATE_DNBUSY;
            report.poll_timeout_ms = dev->poll_timeout_ms;
        }
    } else if (dev->state == DFU_STATE_MANIFEST_SYNC) {
        dev->state = DFU_STATE_MANIFEST;
        report.state = DFU_STATE_MANIFEST;
        report.poll_timeout_ms = dev->poll_timeout_ms;
    }

    dfu_pack_status(&report, dev->reply);
    *out = dev->reply;
    *out_len = DFU_GETSTATUS_LEN;
    return 0;
}

int dfu_control_request(dfu_device_t *dev,
                        uint8_t request, uint16_t block_num, uint16_t length,
                        const uint8_t *data, size_t data_len,
                        const uint8_t **out, size_t *out_len)
{
    *out = NULL;
    *out_len = 0u;

    switch (request) {
    case DFU_DETACH:
        /* У завантажувачі DETACH безглуздий: ми вже тут. Цей запит обробляє
           польотна прошивка через boot_trigger_handle_detach(). */
        return fail(dev, DFU_ERR_STALLEDPKT);

    case DFU_DNLOAD:
        return handle_dnload(dev, block_num, data, data_len);

    case DFU_UPLOAD:
        return handle_upload(dev, block_num, length, out, out_len);

    case DFU_GETSTATUS:
        return handle_getstatus(dev, out, out_len);

    case DFU_CLRSTATUS:
        if (dev->state != DFU_STATE_ERROR) {
            return fail(dev, DFU_ERR_STALLEDPKT);
        }
        dev->status = DFU_OK;
        dev->state = DFU_STATE_IDLE;
        return 0;

    case DFU_GETSTATE:
        dev->reply[0] = (uint8_t)dev->state;
        *out = dev->reply;
        *out_len = 1u;
        return 0;

    case DFU_ABORT:
        if (dev->state == DFU_STATE_ERROR) {
            return fail(dev, DFU_ERR_STALLEDPKT);
        }
        dev->op = DFU_OP_NONE;
        dev->state = DFU_STATE_IDLE;
        return 0;

    default:
        return fail(dev, DFU_ERR_STALLEDPKT);
    }
}

void dfu_poll(dfu_device_t *dev)
{
    dfu_status_t status;

    if (dev->state == DFU_STATE_DNBUSY) {
        switch (dev->op) {
        case DFU_OP_WRITE:
            status = flash_program(dev->op_address, dev->buffer, dev->op_length);
            break;
        case DFU_OP_ERASE:
            status = flash_erase_sector(dev->op_address);
            break;
        case DFU_OP_ERASE_APP:
            status = flash_erase_application();
            break;
        default:
            status = DFU_ERR_UNKNOWN;
            break;
        }

        dev->op = DFU_OP_NONE;
        if (status != DFU_OK) {
            (void)fail(dev, status);
            return;
        }
        dev->state = DFU_STATE_DNLOAD_IDLE;
        return;
    }

    if (dev->state == DFU_STATE_MANIFEST) {
        dev->op = DFU_OP_NONE;
        if (!flash_app_image_valid()) {
            /* Образ побитий: у застосунок не стрибаємо, лишаємось у DFU. */
            (void)fail(dev, DFU_ERR_FIRMWARE);
            return;
        }
        /* bitManifestationTolerant = 0 — далі лише через скидання. */
        dev->state = DFU_STATE_MANIFEST_WAIT_RESET;
        boot_trigger_reset();
    }
}
