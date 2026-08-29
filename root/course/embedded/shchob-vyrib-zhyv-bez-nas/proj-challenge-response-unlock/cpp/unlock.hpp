#pragma once

#include <array>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "hal.hpp"
#include "log.hpp"

namespace eolboot {

inline constexpr std::size_t NonceLen = 32;
inline constexpr std::size_t SignatureLen = 64;
inline constexpr std::size_t PublicKeyLen = 32;

/* Підписується саме склейка Nonce || Chip_UUID */
inline constexpr std::size_t ChallengeMsgLen = NonceLen + ChipUuidLen;

inline constexpr std::uint32_t SessionTimeoutMs = 120'000;

enum class UnlockError : std::uint8_t {
    AlreadyUnlocked = 1,
    NoSession       = 2,
    SessionExpired  = 3,
    BadSignature    = 4,
    WipeFailed      = 5,
    EfuseFailed     = 6,
};

std::string_view describe(UnlockError error) noexcept;

/*
 * Буфер, який затирає себе на виході з області видимості. Звичайний масив
 * оптимізатор чистити не став би: запис у мертву змінну він викидає.
 */
template <std::size_t N>
class SecureBuffer {
public:
    SecureBuffer() = default;
    ~SecureBuffer() noexcept { wipe(); }

    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;

    void wipe() noexcept
    {
        volatile std::uint8_t* p = data_.data();
        for (std::size_t i = 0; i < N; ++i) {
            p[i] = 0x00;
        }
    }

    [[nodiscard]] std::span<std::uint8_t, N> bytes() noexcept { return data_; }
    [[nodiscard]] std::span<const std::uint8_t, N> bytes() const noexcept { return data_; }

private:
    std::array<std::uint8_t, N> data_{};
};

class UnlockController {
public:
    UnlockController(Hal& hal, Log log) noexcept : hal_(hal), log_(log) {}

    /* Генерує Nonce у SRAM і віддає склейку Nonce || Chip_UUID для хоста */
    [[nodiscard]] std::array<std::uint8_t, ChallengeMsgLen> make_challenge();

    /* Верифікація підпису, стирання NVS і перепалювання eFuse — у цьому порядку */
    [[nodiscard]] std::expected<void, UnlockError> execute(
        std::span<const std::uint8_t, SignatureLen> signature);

    /* Гасить сесію, коли вийшов її час життя */
    void drop_expired();

private:
    [[nodiscard]] bool session_expired(std::uint32_t now_ms) const noexcept;
    void forget_session() noexcept;

    [[nodiscard]] std::expected<void, UnlockError> zeroize_user_data();
    [[nodiscard]] std::expected<void, UnlockError> zeroize_sector(std::uint32_t addr);

    Hal& hal_;
    Log log_;
    SecureBuffer<ChallengeMsgLen> session_msg_{}; // Nonce || Chip_UUID, лише в SRAM
    std::uint32_t started_ms_{ 0 };
    bool active_{ false };
};

} // namespace eolboot
