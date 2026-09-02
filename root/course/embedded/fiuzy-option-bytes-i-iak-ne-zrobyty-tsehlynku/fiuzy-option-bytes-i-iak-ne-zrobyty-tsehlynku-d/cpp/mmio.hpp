#pragma once

#include <cstdint>
#include <type_traits>

// Доступ до периферії STM32G4 (RM0440): блоки регістрів і бітові прапорці,
// які має сенс тримати типізованими. Розкладка самого слова OPTR живе не тут,
// а поруч зі значенням, яке вона кодує — див. option_config.hpp.
namespace hal {

// Дозвіл на побітові операції вмикається для конкретного scoped enum, а не
// для всіх підряд: інакше типізація прапорців нічого не боронила б.
template <class E>
struct is_flags : std::false_type {};

template <class E>
inline constexpr bool is_flags_v = is_flags<E>::value;

template <class E>
    requires is_flags_v<E>
constexpr std::uint32_t raw(E value) noexcept
{
    return static_cast<std::uint32_t>(value);
}

template <class E>
    requires is_flags_v<E>
constexpr E operator|(E a, E b) noexcept
{
    return static_cast<E>(raw(a) | raw(b));
}

struct FlashBlock {
    volatile std::uint32_t ACR;       // 0x00
    volatile std::uint32_t PDKEYR;    // 0x04
    volatile std::uint32_t KEYR;      // 0x08
    volatile std::uint32_t OPTKEYR;   // 0x0C
    volatile std::uint32_t SR;        // 0x10
    volatile std::uint32_t CR;        // 0x14
    volatile std::uint32_t ECCR;      // 0x18
    volatile std::uint32_t reserved0; // 0x1C
    volatile std::uint32_t OPTR;      // 0x20
};

struct PwrBlock {
    volatile std::uint32_t CR1; // 0x00
    volatile std::uint32_t CR2; // 0x04  PVDE, PVDLS
    volatile std::uint32_t CR3; // 0x08
    volatile std::uint32_t CR4; // 0x0C
    volatile std::uint32_t SR1; // 0x10
    volatile std::uint32_t SR2; // 0x14  PVDO
};

// reinterpret_cast не буває constexpr, тому доступ — через inline-функції.
inline FlashBlock& flash() noexcept
{
    return *reinterpret_cast<FlashBlock*>(0x4002'2000UL);
}

inline PwrBlock& pwr() noexcept
{
    return *reinterpret_cast<PwrBlock*>(0x4000'7000UL);
}

inline volatile std::uint32_t& rcc_apb1enr1() noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(0x4002'1000UL + 0x58UL);
}

inline constexpr std::uint32_t kRccPwrEn = 1UL << 28;

// Магічні ключі; порядок запису критичний.
inline constexpr std::uint32_t kFlashKey1  = 0x4567'0123UL;
inline constexpr std::uint32_t kFlashKey2  = 0xCDEF'89ABUL;
inline constexpr std::uint32_t kOptKey1    = 0x0819'2A3BUL;
inline constexpr std::uint32_t kOptKey2    = 0x4C5D'6E7FUL;

enum class FlashCr : std::uint32_t {
    OptStart  = 1UL << 17,
    OblLaunch = 1UL << 27,
    OptLock   = 1UL << 30,
    Lock      = 1UL << 31,
};

enum class FlashSr : std::uint32_t {
    Eop      = 1UL << 0,
    OpErr    = 1UL << 1,
    ProgErr  = 1UL << 3,
    WrpErr   = 1UL << 4,
    PgaErr   = 1UL << 5,
    SizeErr  = 1UL << 6,
    PgsErr   = 1UL << 7,
    MisErr   = 1UL << 8,
    FastErr  = 1UL << 9,
    OptvErr  = 1UL << 15,
    Busy     = 1UL << 16,
};

enum class PwrCr2 : std::uint32_t {
    PvdEnable = 1UL << 0,
};

enum class PwrSr2 : std::uint32_t {
    PvdOutput = 1UL << 11, // 1 = VDD нижче обраного порога
};

template <> struct is_flags<FlashCr> : std::true_type {};
template <> struct is_flags<FlashSr> : std::true_type {};
template <> struct is_flags<PwrCr2>  : std::true_type {};
template <> struct is_flags<PwrSr2>  : std::true_type {};

inline constexpr std::uint32_t kFlashSrErrors =
    raw(FlashSr::OpErr | FlashSr::ProgErr | FlashSr::WrpErr | FlashSr::PgaErr |
        FlashSr::SizeErr | FlashSr::PgsErr | FlashSr::MisErr | FlashSr::FastErr |
        FlashSr::OptvErr);

inline constexpr std::uint32_t kPvdLevelShift = 1;
inline constexpr std::uint32_t kPvdLevelMask  = 0x7UL << kPvdLevelShift;

inline bool flash_busy() noexcept
{
    return (flash().SR & raw(FlashSr::Busy)) != 0UL;
}

} // namespace hal
