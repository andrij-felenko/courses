// system_bus.hpp — системна шина, адресний дешифратор і периферія.
//
// Дешифратор винесено в чисту constexpr-функцію: за адресою вона каже, який
// кристал вибрано, і що саме подано йому на входи. Кристали розділені й у
// типах — ROM лежить в окремому масиві, тож запис у нього неможливий
// структурно, а не «завдяки перевірці».
//
// Помилки шини не друкуються тут: read і write повертають std::expected,
// а вирішує, що з помилкою робити, ядро — саме воно в залізі й ловить BusFault.
#pragma once

#include <array>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <variant>

namespace emu {

inline constexpr std::size_t   kRomSize   = 0x4000;   // 0x0000–0x3FFF
inline constexpr std::size_t   kRamSize   = 0x4000;   // 0x4000–0x7FFF
inline constexpr std::uint16_t kRamBase   = 0x4000;
inline constexpr std::uint16_t kMmioBase  = 0x8000;   // 0x8000–0xBFFF
inline constexpr std::uint16_t kMmioLimit = 0xC000;   // далі не підключено нічого

inline constexpr std::uint16_t kRegGpioOut = 0x8000;  // біт 0 — світлодіод
inline constexpr std::uint16_t kRegGpioIn  = 0x8001;  // біт 0 — кнопка з підтяжкою

// Що читає ядро, коли на адресу не відповів жоден кристал.
inline constexpr std::uint8_t kOpenBus = 0xFF;

// Результат роботи адресного дешифратора.
struct RomCell  { std::uint16_t offset; };
struct RamCell  { std::uint16_t offset; };
struct MmioReg  { std::uint16_t index; bool ghost; };  // всередині кристала розібрано лише A0
struct NoDevice {};

using Selected = std::variant<RomCell, RamCell, MmioReg, NoDevice>;

[[nodiscard]] constexpr Selected decode_address(std::uint16_t addr) noexcept
{
    if (addr < kRamBase) {
        return RomCell{addr};
    }
    if (addr < kMmioBase) {
        return RamCell{static_cast<std::uint16_t>(addr - kRamBase)};
    }
    if (addr < kMmioLimit) {
        // Неповна дешифрація: регістрів рівно два, і вони фантомними копіями
        // повторюються по всій області кристала периферії.
        const std::uint16_t index = addr & 0x0001;
        return MmioReg{index, addr != static_cast<std::uint16_t>(kMmioBase | index)};
    }
    return NoDevice{};
}

enum class BusFault : std::uint8_t {
    RomWrite,          // лінія /WR до кристала програм не підведена
    ReadOnlyRegister,  // порт вводу — буфер, писати в нього нема куди
    NoDevice           // жоден /CS не активний
};

[[nodiscard]] constexpr std::string_view describe(BusFault fault) noexcept
{
    switch (fault) {
        case BusFault::RomWrite:         return "запис у ROM";
        case BusFault::ReadOnlyRegister: return "запис у регістр лише для читання";
        case BusFault::NoDevice:         return "за адресою немає кристала";
    }
    return "невідома помилка шини";
}

class SystemBus {
public:
    // Заливка прошивки в кристал програм. Образ, більший за ROM, — це помилка
    // складання стенда, а не робочий стан: далі запускати нема чого.
    void load_rom(std::span<const std::uint8_t> image);

    [[nodiscard]] std::expected<std::uint8_t, BusFault> read(std::uint16_t addr);
    std::expected<void, BusFault>                      write(std::uint16_t addr, std::uint8_t data);

    // Погляд збоку для трасування: без шинного циклу й без побічних дій.
    [[nodiscard]] std::uint8_t peek(std::uint16_t addr) const noexcept;

    // Кнопку натискають після заданої кількості опитувань порту вводу.
    void press_button_after(unsigned polls) noexcept;

    void set_trace(bool on) noexcept { trace_ = on; }

    [[nodiscard]] std::uint8_t   gpio_out_latch() const noexcept { return gpio_out_latch_; }
    [[nodiscard]] bool           led_on() const noexcept { return (gpio_out_latch_ & 0x01) != 0; }
    [[nodiscard]] unsigned long  cycles() const noexcept { return cycles_; }
    [[nodiscard]] std::uint8_t   ram_at(std::uint16_t addr) const noexcept;

private:
    [[nodiscard]] std::uint8_t read_mmio(std::uint16_t addr, const MmioReg& reg);
    std::expected<void, BusFault> write_mmio(std::uint16_t addr, const MmioReg& reg, std::uint8_t data);
    void report_ghost(std::uint16_t addr, const MmioReg& reg) const;

    std::array<std::uint8_t, kRomSize> rom_{};
    std::array<std::uint8_t, kRamSize> ram_{};

    std::uint8_t  gpio_out_latch_{0x00};
    std::uint8_t  gpio_in_pins_{0x01};      // кнопка відпущена: підтяжка тримає одиницю
    unsigned      button_polls_{0};
    unsigned      press_after_{~0u};        // за замовчуванням кнопку не натискають
    unsigned long cycles_{0};
    bool          trace_{true};
};

}  // namespace emu
