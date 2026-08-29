#include <array>
#include <cstdint>
#include <span>

#include "frame.hpp"
#include "hal.hpp"
#include "log.hpp"
#include "unlock.hpp"

namespace eolboot {
namespace {

void reply_status(Hal& hal, std::uint8_t code)
{
    const std::array<std::uint8_t, 1> payload{ code };
    send_frame(hal, Cmd::Status, payload);
}

void handle_get_challenge(Hal& hal, Log& log, UnlockController& unlock)
{
    log.line("CMD_GET_CHALLENGE received");

    const auto msg = unlock.make_challenge();
    log.hex("TRNG entropy pool ready. Nonce: ", std::span{ msg }.first(NonceLen));
    log.dec("Challenge session started. Timeout: ", SessionTimeoutMs, " ms.");

    send_frame(hal, Cmd::Challenge, msg);
}

void handle_unlock_execute(Hal& hal, Log& log, UnlockController& unlock, const Frame& frame)
{
    log.dec("CMD_UNLOCK_EXECUTE received. Signature len: ",
            static_cast<std::uint32_t>(frame.payload.size()), " bytes.");

    if (frame.payload.size() != SignatureLen) {
        log.line("Rejected: signature length mismatch.");
        reply_status(hal, static_cast<std::uint8_t>(UnlockError::BadSignature));
        return;
    }

    const auto result = unlock.execute(frame.payload.first<SignatureLen>());

    if (!result) {
        log.line(describe(result.error()));
        reply_status(hal, static_cast<std::uint8_t>(result.error()));
        return;
    }

    log.line("System status changed: UNLOCKED_DEV_MODE.");
    reply_status(hal, 0);
    log.line("Rebooting into open bootloader...");
    hal.reboot();
}

void dispatch(Hal& hal, Log& log, UnlockController& unlock, const Frame& frame)
{
    switch (frame.cmd) {
    case Cmd::GetChallenge:
        handle_get_challenge(hal, log, unlock);
        break;
    case Cmd::UnlockExecute:
        handle_unlock_execute(hal, log, unlock, frame);
        break;
    default:
        log.dec("Unknown command ", static_cast<std::uint32_t>(frame.cmd), " ignored.");
        break;
    }
}

} // namespace
} // namespace eolboot

int main()
{
    using namespace eolboot;

    Hal& hal = board_hal();
    Log log{ hal };

    std::array<std::uint8_t, ChipUuidLen> uuid{};
    hal.read_chip_uuid(uuid);
    log.hex("Device UUID: ", uuid);
    log.line(hal.efuse_unlocked() ? "Mode: UNLOCKED_DEV_MODE" : "Mode: SECURE_BOOT_LOCKED");

    UnlockController unlock{ hal, log };
    FrameDecoder decoder;

    for (;;) {
        const std::uint32_t now = hal.tick_ms();

        if (const auto byte = hal.read_byte()) {
            if (const auto decoded = decoder.push(*byte, now)) {
                if (decoded->has_value()) {
                    dispatch(hal, log, unlock, decoded->value());
                } else {
                    log.line(describe(decoded->error()));
                }
            }
        }

        decoder.drop_stale(now);
        unlock.drop_expired();
    }
}
