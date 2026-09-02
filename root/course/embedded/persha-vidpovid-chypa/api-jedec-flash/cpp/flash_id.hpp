#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "spi_link.hpp"

namespace flash {

inline constexpr std::uint8_t kCmdReadId      = 0x9F;
inline constexpr std::uint8_t kCmdReadStatus1 = 0x05;
inline constexpr std::uint8_t kCmdExitQpi     = 0xFF;
inline constexpr std::uint8_t kStatusWip      = 0x01;

inline constexpr std::size_t kIdMaxBytes      = 6;   /* 3 паспортні байти + запас на банки */
inline constexpr std::size_t kMaxContinuation = 3;
inline constexpr unsigned    kSafeClockHz     = 20'000'000;  /* нижче межі 33–50 МГц для 0x9F */
inline constexpr std::chrono::milliseconds kWipTimeout{4000};

/* Аварійні стани шини — це не «дивний виробник», а діагнози заліза. */
enum class IdError {
    ShortAnswer,
    StuckHigh,          /* суцільні 0xFF: обрив MISO, немає живлення або чип у QPI */
    StuckLow,           /* суцільні 0x00: замикання MISO на землю */
    Continuation,       /* потік 0x7F без кінця */
    StillBusy,          /* WIP не скинувся за тайм-аут */
    UnknownCapacity     /* код ємності поза 0x10..0x1A */
};

[[nodiscard]] std::string_view describe(IdError error) noexcept;

struct Passport {
    std::array<std::uint8_t, kIdMaxBytes> raw{};
    std::size_t   raw_len{0};
    std::uint8_t  bank{1};            /* 1 + кількість байтів продовження 0x7F */
    std::uint8_t  manufacturer{0};
    std::uint8_t  memory_type{0};
    std::uint8_t  capacity_code{0};
    std::uint32_t size_bytes{0};      /* 2^capacity_code */
    std::uint32_t page_size{256};     /* квант програмування */
    std::uint32_t sector_size{4096};  /* мінімальне стирання */
    bool          recovered_from_qpi{false};

    [[nodiscard]] std::uint32_t pages() const noexcept { return size_bytes / page_size; }
    [[nodiscard]] std::uint32_t sectors() const noexcept { return size_bytes / sector_size; }
    [[nodiscard]] std::string_view vendor() const noexcept;
};

/* Назва виробника за JEP106 осмислена лише разом із номером банку. */
[[nodiscard]] std::string_view vendor_name(std::uint8_t bank, std::uint8_t manufacturer) noexcept;

/* Розбір готової відповіді. Помилка несе ще й те, що встигло розібратися:
   для звіту bring-up сирі байти важать не менше за діагноз. */
[[nodiscard]] std::expected<Passport, IdError> decode(std::span<const std::uint8_t> answer);

/* Повний цикл опитування з усіма запобіжниками розділу 5. */
[[nodiscard]] std::expected<Passport, IdError> identify(SpiLink &link);

}  // namespace flash
