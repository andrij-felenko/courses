#include "frame.h"
#include "hal.h"
#include "log.h"
#include "unlock.h"

static void handle_get_challenge(void)
{
    uint8_t msg[CHALLENGE_MSG_LEN];

    log_line("CMD_GET_CHALLENGE received");
    unlock_create_challenge(msg);

    log_hex("TRNG entropy pool ready. Nonce: ", msg, CHALLENGE_NONCE_LEN);
    log_u32("Challenge session started. Timeout: ", UNLOCK_SESSION_TIMEOUT_MS, " ms.");

    frame_send(CMD_CHALLENGE, msg, (uint16_t)sizeof msg);
}

static void handle_unlock_execute(const frame_t *frame)
{
    log_u32("CMD_UNLOCK_EXECUTE received. Signature len: ", frame->len, " bytes.");

    if (frame->len != SIGNATURE_LEN) {
        const uint8_t code = (uint8_t)UNLOCK_ERR_BAD_SIG;
        log_line("Rejected: signature length mismatch.");
        frame_send(CMD_STATUS, &code, 1);
        return;
    }

    const unlock_status_t status = unlock_execute(frame->payload);
    const uint8_t code = (uint8_t)status;

    log_line(unlock_status_text(status));
    frame_send(CMD_STATUS, &code, 1);

    if (status == UNLOCK_OK) {
        log_line("Rebooting into open bootloader...");
        hal_reboot();
    }
}

static void dispatch(const frame_t *frame)
{
    switch (frame->cmd) {
    case CMD_GET_CHALLENGE:
        handle_get_challenge();
        break;
    case CMD_UNLOCK_EXECUTE:
        handle_unlock_execute(frame);
        break;
    default:
        log_u32("Unknown command 0x", frame->cmd, " ignored.");
        break;
    }
}

int main(void)
{
    uint8_t uuid[CHIP_UUID_LEN];
    hal_get_chip_uuid(uuid);

    log_hex("Device UUID: ", uuid, sizeof uuid);
    log_line(hal_efuse_read_unlocked() ? "Mode: UNLOCKED_DEV_MODE"
                                       : "Mode: SECURE_BOOT_LOCKED");

    frame_rx_t rx;
    frame_t frame;
    frame_rx_init(&rx);

    for (;;) {
        const uint32_t now = hal_get_tick_ms();
        uint8_t byte = 0;

        if (hal_uart_read_byte(&byte)) {
            switch (frame_rx_push(&rx, byte, now, &frame)) {
            case FRAME_RX_DONE:
                dispatch(&frame);
                break;
            case FRAME_RX_BAD_CRC:
                log_line("Frame dropped: CRC mismatch.");
                break;
            case FRAME_RX_OVERFLOW:
                log_line("Frame dropped: payload too long.");
                break;
            case FRAME_RX_PENDING:
            default:
                break;
            }
        }

        frame_rx_watchdog(&rx, now);
        unlock_tick(now);
    }
}
