// Сеанс завантаження образу: бітова карта блоків, карта вже стертих секторів
// і момент завершення. Про USB тут не знають нічого.
#pragma once

#include "uf2_block.hpp"

#include <bitset>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <variant>

namespace uf2 {

inline constexpr std::uint32_t FlashSectorSize = 4096; // гранула стирання NOR Flash

// 8192 блоки × 256 байтів = 2 МіБ образу; 4096 секторів × 4 КіБ = 16 МіБ простору.
inline constexpr std::size_t MaxBlocks  = 8192;
inline constexpr std::size_t MaxSectors = 4096;

enum class SessionError : std::uint8_t {
    BlockCountMismatch, // два блоки одного сеансу кажуть різне numBlocks
    ImageTooLarge,      // образ не вміщається у бітову карту
    AddressOutOfMap,    // адреса поза картою стертих секторів
    EraseFailed,
    ProgramFailed,
};

using AcceptError = std::variant<ParseError, SessionError>;

// true, якщо це просто чужий сектор файлової системи, а не збій.
[[nodiscard]] bool isForeignSector(const AcceptError& e) noexcept;
[[nodiscard]] std::string_view describe(const AcceptError& e) noexcept;

// Контракт порту: реалізується під конкретний кристал (див. msc_bridge.cpp).
namespace port {
[[nodiscard]] bool eraseSector(std::uint32_t address) noexcept;
[[nodiscard]] bool program(std::uint32_t address, std::span<const std::uint8_t> data) noexcept;
} // namespace port

class DownloadSession {
public:
    struct Progress {
        std::uint32_t handled;
        std::uint32_t total; // 0, поки не прийшов перший блок
        bool          complete;
    };

    DownloadSession(std::uint32_t familyId, FlashRegion flash) noexcept
        : familyId_{familyId}, flash_{flash} {}

    // Головний вхід: сирий сектор від USB.
    [[nodiscard]] std::expected<Progress, AcceptError>
    accept(std::span<const std::uint8_t> sector) noexcept;

    [[nodiscard]] Progress progress() const noexcept;

private:
    [[nodiscard]] std::expected<void, SessionError>
    ensureErased(std::uint32_t address, std::uint32_t length) noexcept;

    void markHandled(std::uint32_t index) noexcept;

    std::uint32_t familyId_;
    FlashRegion   flash_;
    std::uint32_t totalBlocks_{0};
    std::uint32_t handledBlocks_{0};
    std::bitset<MaxBlocks>  written_{};
    std::bitset<MaxSectors> erased_{};
};

} // namespace uf2
