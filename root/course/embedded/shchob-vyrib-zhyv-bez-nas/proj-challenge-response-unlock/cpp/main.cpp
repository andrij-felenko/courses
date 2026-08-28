#include <array>
#include <span>
#include <cstdint>
#include <expected>
#include <algorithm>

namespace bootloader {

inline constexpr std::size_t ChallengeNonceLen = 32;
inline constexpr std::size_t ChipUuidLen = 16;
inline constexpr std::size_t SignatureLen = 64;
inline constexpr std::size_t PublicKeyLen = 32;
inline constexpr std::size_t NvsSectorSize = 4096;
inline constexpr std::size_t NvsSectorsCount = 8;
inline constexpr uint32_t ChallengeTimeoutMs = 120'000;

enum class UnlockError : uint8_t {
    InvalidNonce,
    SignatureVerificationFailed,
    ChallengeTimedOut,
    FlashEraseFailed,
    EfuseBurnFailed
};

/* RAII-обгортка для гарантованого стирання чутливих даних у пам'яті */
template <std::size_t N>
struct SecureBuffer {
    std::array<uint8_t, N> data{};

    ~SecureBuffer() noexcept {
        volatile uint8_t* ptr = data.data();
        std::fill_n(ptr, N, 0x00);
    }
};

/* Апаратний інтерфейс мікроконтролера */
class HalDriver {
public:
    virtual ~HalDriver() = default;
    virtual void fill_trng(std::span<uint8_t> dest) = 0;
    virtual void read_chip_uuid(std::span<uint8_t, ChipUuidLen> dest) = 0;
    virtual uint32_t get_tick_ms() const noexcept = 0;
    virtual bool erase_flash_sector(uint32_t address) = 0;
    virtual bool write_flash(uint32_t address, std::span<const uint8_t> buffer) = 0;
    virtual bool burn_unlocked_efuse() = 0;
    virtual bool verify_ed25519(std::span<const uint8_t, SignatureLen> sig,
                                std::span<const uint8_t> msg,
                                std::span<const uint8_t, PublicKeyLen> pubkey) const noexcept = 0;
};

class UnlockController {
public:
    explicit UnlockController(HalDriver& hal, std::span<const uint8_t, PublicKeyLen> root_pubkey) noexcept
        : hal_(hal), root_pubkey_(root_pubkey) {}

    struct Challenge {
        std::array<uint8_t, ChallengeNonceLen> nonce;
        std::array<uint8_t, ChipUuidLen> uuid;
    };

    [[nodiscard]] Challenge generate_challenge() {
        hal_.fill_trng(active_challenge_.nonce);
        hal_.read_chip_uuid(active_challenge_.uuid);
        challenge_created_at_ms_ = hal_.get_tick_ms();
        has_active_challenge_ = true;

        return {active_challenge_.nonce, active_challenge_.uuid};
    }

    [[nodiscard]] std::expected<void, UnlockError> process_unlock(
        std::span<const uint8_t, SignatureLen> signature, uint32_t now_ms) noexcept {
        
        if (!has_active_challenge_) {
            return std::unexpected(UnlockError::ChallengeTimedOut);
        }

        if (now_ms - challenge_created_at_ms_ > ChallengeTimeoutMs) {
            reset_challenge();
            return std::unexpected(UnlockError::ChallengeTimedOut);
        }

        SecureBuffer<ChallengeNonceLen + ChipUuidLen> msg_buf;
        std::copy(active_challenge_.nonce.begin(), active_challenge_.nonce.end(), msg_buf.data.begin());
        std::copy(active_challenge_.uuid.begin(), active_challenge_.uuid.end(), msg_buf.data.begin() + ChallengeNonceLen);

        const bool is_valid = hal_.verify_ed25519(signature, msg_buf.data, root_pubkey_);
        reset_challenge();

        if (!is_valid) {
            return std::unexpected(UnlockError::SignatureVerificationFailed);
        }

        if (!zeroize_user_data()) {
            return std::unexpected(UnlockError::FlashEraseFailed);
        }

        if (!hal_.burn_unlocked_efuse()) {
            return std::unexpected(UnlockError::EfuseBurnFailed);
        }

        return {};
    }

private:
    void reset_challenge() noexcept {
        volatile uint8_t* ptr = reinterpret_cast<volatile uint8_t*>(&active_challenge_);
        std::fill_n(ptr, sizeof(active_challenge_), 0x00);
        has_active_challenge_ = false;
    }

    bool zeroize_user_data() noexcept {
        constexpr uint32_t NvsBaseAddr = 0x08040000;
        const std::array<uint8_t, 256> zeros{};

        for (std::size_t i = 0; i < NvsSectorsCount; ++i) {
            const uint32_t sector_addr = NvsBaseAddr + static_cast<uint32_t>(i * NvsSectorSize);
            if (!hal_.erase_flash_sector(sector_addr)) {
                return false;
            }
            for (uint32_t offset = 0; offset < NvsSectorSize; offset += zeros.size()) {
                if (!hal_.write_flash(sector_addr + offset, zeros)) {
                    return false;
                }
            }
        }
        return true;
    }

    HalDriver& hal_;
    std::span<const uint8_t, PublicKeyLen> root_pubkey_;
    struct {
        std::array<uint8_t, ChallengeNonceLen> nonce{};
        std::array<uint8_t, ChipUuidLen> uuid{};
    } active_challenge_;
    uint32_t challenge_created_at_ms_{0};
    bool has_active_challenge_{false};
};

} // namespace bootloader
