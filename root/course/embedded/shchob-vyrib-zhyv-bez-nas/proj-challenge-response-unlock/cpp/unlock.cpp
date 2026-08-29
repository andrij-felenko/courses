#include "unlock.hpp"

#include <algorithm>

/*
 * Верифікацію підпису дає TweetNaCl (tweetnacl.c/tweetnacl.h кладемо в проєкт):
 *   int crypto_sign_open(u8 *m, u64 *mlen, const u8 *sm, u64 n, const u8 *pk);
 * Це Ed25519 за RFC 8032; приймає лише "приєднаний" підпис sm = sig || msg.
 */
extern "C" {
#include "tweetnacl.h"
}

namespace eolboot {
namespace {

/* Відкритий кореневий ключ розблокування виробника (зашитий у Mask ROM) */
constexpr std::array<std::uint8_t, PublicKeyLen> EolRootPublicKey{
    0x3b, 0x6a, 0x27, 0xbc, 0xce, 0xb6, 0xa4, 0x2d,
    0x68, 0x7a, 0xa5, 0x65, 0x84, 0x88, 0xdd, 0x4d,
    0x9c, 0x86, 0x45, 0x40, 0x07, 0x69, 0x66, 0x04,
    0x69, 0x62, 0x0d, 0xa4, 0x63, 0xa5, 0x72, 0x8b
};

bool verify_ed25519(std::span<const std::uint8_t, SignatureLen> signature,
                    std::span<const std::uint8_t, ChallengeMsgLen> message)
{
    SecureBuffer<SignatureLen + ChallengeMsgLen> attached;
    SecureBuffer<SignatureLen + ChallengeMsgLen> opened;

    std::ranges::copy(signature, attached.bytes().begin());
    std::ranges::copy(message, attached.bytes().begin() + SignatureLen);

    unsigned long long opened_len = 0;
    const int rc = crypto_sign_open(opened.bytes().data(), &opened_len,
                                    attached.bytes().data(), attached.bytes().size(),
                                    EolRootPublicKey.data());

    return rc == 0 && opened_len == ChallengeMsgLen;
}

} // namespace

std::string_view describe(UnlockError error) noexcept
{
    switch (error) {
    case UnlockError::AlreadyUnlocked: return "Rejected: device is already unlocked.";
    case UnlockError::NoSession:       return "Rejected: no active challenge.";
    case UnlockError::SessionExpired:  return "Rejected: challenge session timed out.";
    case UnlockError::BadSignature:    return "Rejected: signature verification failed.";
    case UnlockError::WipeFailed:      return "Aborted: NVS zeroization failed, device stays locked.";
    case UnlockError::EfuseFailed:     return "Aborted: eFuse burn failed after zeroization.";
    }
    return "Rejected: unknown error.";
}

bool UnlockController::session_expired(std::uint32_t now_ms) const noexcept
{
    /* Різниця беззнакових коректна й на переповненні лічильника тіків */
    return now_ms - started_ms_ > SessionTimeoutMs;
}

void UnlockController::forget_session() noexcept
{
    session_msg_.wipe();
    active_ = false;
    started_ms_ = 0;
}

std::array<std::uint8_t, ChallengeMsgLen> UnlockController::make_challenge()
{
    auto msg = session_msg_.bytes();
    hal_.fill_random(msg.first<NonceLen>());
    hal_.read_chip_uuid(msg.subspan<NonceLen>().first<ChipUuidLen>());

    started_ms_ = hal_.tick_ms();
    active_ = true;

    std::array<std::uint8_t, ChallengeMsgLen> copy{};
    std::ranges::copy(msg, copy.begin());
    return copy;
}

void UnlockController::drop_expired()
{
    if (active_ && session_expired(hal_.tick_ms())) {
        forget_session();
        log_.line("Challenge session expired. Nonce discarded.");
    }
}

/*
 * Стирання переводить біти в 0xFF — залишковий заряд у зношених комірках
 * плаваючого затвора з нього ще відновлюють. Тому другим проходом пишемо нулі
 * і читаємо назад: мовчазна відмова запису не має видатися успіхом.
 */
std::expected<void, UnlockError> UnlockController::zeroize_sector(std::uint32_t addr)
{
    static constexpr std::array<std::uint8_t, 128> Zeros{};
    std::array<std::uint8_t, 128> check{};

    log_.addr("Erasing NVS sector 0x", addr, "...");
    if (!hal_.erase_sector(addr)) {
        return std::unexpected(UnlockError::WipeFailed);
    }

    for (std::uint32_t off = 0; off < NvsSectorSize; off += Zeros.size()) {
        if (!hal_.write_flash(addr + off, Zeros)) {
            return std::unexpected(UnlockError::WipeFailed);
        }
    }

    for (std::uint32_t off = 0; off < NvsSectorSize; off += check.size()) {
        if (!hal_.read_flash(addr + off, check)) {
            return std::unexpected(UnlockError::WipeFailed);
        }
        if (std::ranges::any_of(check, [](std::uint8_t b) { return b != 0x00; })) {
            return std::unexpected(UnlockError::WipeFailed);
        }
    }

    log_.line("[OK] Overwriting zeros... [OK]");
    return {};
}

std::expected<void, UnlockError> UnlockController::zeroize_user_data()
{
    for (std::uint32_t i = 0; i < NvsSectorsCount; ++i) {
        if (auto done = zeroize_sector(NvsBaseAddr + i * NvsSectorSize); !done) {
            return done;
        }
    }

    log_.dec("Zeroization completed (", NvsSectorsCount * NvsSectorSize / 1024, " KB sanitized).");
    return {};
}

std::expected<void, UnlockError> UnlockController::execute(
    std::span<const std::uint8_t, SignatureLen> signature)
{
    if (hal_.efuse_unlocked()) {
        return std::unexpected(UnlockError::AlreadyUnlocked);
    }
    if (!active_) {
        return std::unexpected(UnlockError::NoSession);
    }
    if (session_expired(hal_.tick_ms())) {
        forget_session();
        return std::unexpected(UnlockError::SessionExpired);
    }

    log_.line("Verifying Ed25519 signature against ROM EOL_ROOT_PUBLIC_KEY...");
    const bool valid = verify_ed25519(signature, session_msg_.bytes());

    /* Nonce одноразовий: після спроби він більше не дійсний ні за яких умов */
    forget_session();

    if (!valid) {
        return std::unexpected(UnlockError::BadSignature);
    }

    log_.line("Signature OK. Proceeding to Secure Zeroization.");
    if (auto wiped = zeroize_user_data(); !wiped) {
        /* Секрети могли вціліти наполовину — eFuse не чіпаємо */
        return wiped;
    }

    log_.line("Burning UNLOCKED eFuse bit...");
    if (!hal_.burn_unlocked_efuse()) {
        return std::unexpected(UnlockError::EfuseFailed);
    }

    return {};
}

} // namespace eolboot
