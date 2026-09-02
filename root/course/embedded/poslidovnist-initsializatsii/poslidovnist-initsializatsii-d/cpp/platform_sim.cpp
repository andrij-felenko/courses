#include <algorithm>
#include <array>
#include <cstdint>
#include <print>

#include "platform.hpp"
#include "sensor.hpp"

// Хостова модель стенда: два місця на шині I2C, спільна лінія живлення.
// Модель відтворює саме ті явища, через які ініціалізація й буває складною:
//   - до кінця t_boot чип не підтверджує адресу (NACK);
//   - команда SW_RESET на кілька мілісекунд глушить інтерфейсний блок;
//   - RO-розряди (DRDY, FILT_RDY) живуть усередині робочих регістрів;
//   - у робочому режимі конфігураційні регістри заблоковані від запису;
//   - завада спотворює один запис і збиває автомат інтерфейсу на SDA.
namespace {

using namespace std::chrono_literals;
namespace reg = bringup::reg;
namespace bits = bringup::bits;

constexpr std::size_t kRegCount = 0x20;
constexpr auto kSwResetTime = 8ms;
constexpr auto kSettleTime = 20ms;

struct Chip {
    std::uint8_t addr{};
    bool mounted{};
    bool has_nrst{};
    std::chrono::milliseconds boot{};
    std::array<std::uint8_t, kRegCount> regs{};
    platform::Clock::time_point ready_at{};
    platform::Clock::time_point settled_at{platform::Clock::time_point::max()};
    int glitch_writes{};  // скільки записів попереду зіпсує завада
    bool desync{};        // автомат інтерфейсу збитий і от-от сяде на SDA
};

std::int64_t g_now_ms = 0;
std::int64_t g_micros_acc = 0;
std::array<Chip, 2> g_chips{};
bool g_rail_on = false;
bool g_sda_low = false;
int g_stuck_clocks = 0;
bool g_pins_gpio = false;
bool g_scl_level = true;
unsigned g_watchdog_kicks = 0;

Chip* find_chip(std::uint8_t addr) {
    auto it = std::ranges::find(g_chips, addr, &Chip::addr);
    return it == g_chips.end() ? nullptr : &*it;
}

void chip_boot(Chip& chip, std::chrono::milliseconds delay) {
    chip.regs.fill(0);
    chip.regs[reg::WhoAmI] = bringup::WhoAmIValue;
    chip.regs[reg::Range] = 0x40;  // зарезервований біт 6 завжди читається як 1
    chip.ready_at = platform::Clock::now() + delay;
    chip.settled_at = platform::Clock::time_point::max();
    chip.desync = false;
}

std::expected<Chip*, platform::BusError> bus_precheck(std::uint8_t addr) {
    if (g_sda_low) {
        return std::unexpected(platform::BusError::Stuck);
    }
    if (!g_rail_on) {
        return std::unexpected(platform::BusError::Nack);
    }
    Chip* chip = find_chip(addr);
    if (chip == nullptr || !chip->mounted) {
        return std::unexpected(platform::BusError::Nack);  // ніхто не тягне SDA
    }
    if (platform::Clock::now() < chip->ready_at) {
        return std::unexpected(platform::BusError::Nack);  // усе ще всередині POR
    }
    return chip;
}

}  // namespace

namespace platform {

std::string_view to_string(BusError error) {
    return error == BusError::Nack ? "NACK" : "залипла SDA";
}

Clock::time_point Clock::now() noexcept {
    return Clock::time_point{Clock::duration{g_now_ms}};
}

void sleep(std::chrono::milliseconds duration) { g_now_ms += duration.count(); }

void sleep(std::chrono::microseconds duration) {
    g_micros_acc += duration.count();
    g_now_ms += g_micros_acc / 1000;
    g_micros_acc %= 1000;
}

void watchdog_kick() noexcept { ++g_watchdog_kicks; }

std::expected<std::uint8_t, BusError> I2cBus::read(std::uint8_t dev,
                                                   std::uint8_t reg_addr) noexcept {
    auto chip = bus_precheck(dev);
    if (!chip) {
        return std::unexpected(chip.error());
    }
    if (reg_addr >= kRegCount) {
        return std::unexpected(BusError::Nack);
    }

    Chip& c = **chip;
    std::uint8_t value = c.regs[reg_addr];
    if (reg_addr == reg::Status) {
        value = bits::StatusReady;
        if (Clock::now() >= c.settled_at) {
            value |= bits::StatusDrdy;
        }
    } else if (reg_addr == reg::Filter && Clock::now() >= c.settled_at) {
        value |= bits::FilterReady;  // апаратний RO-прапорець поверх конфігурації
    }

    if (c.desync) {
        // Збитий автомат добиває поточну транзакцію і сідає на лінію даних
        c.desync = false;
        g_sda_low = true;
        g_stuck_clocks = 3;
    }
    return value;
}

std::expected<void, BusError> I2cBus::write(std::uint8_t dev, std::uint8_t reg_addr,
                                            std::uint8_t value) noexcept {
    auto chip = bus_precheck(dev);
    if (!chip) {
        return std::unexpected(chip.error());
    }
    if (reg_addr >= kRegCount) {
        return std::unexpected(BusError::Nack);
    }
    Chip& c = **chip;

    // RO-регістри підтверджують байт, але не зберігають його
    if (reg_addr == reg::WhoAmI || reg_addr == reg::Status) {
        return {};
    }

    if (reg_addr == reg::ResetCtrl && (value & bits::SwReset) != 0) {
        chip_boot(c, kSwResetTime);
        return {};
    }

    if (c.glitch_writes > 0) {
        // Завада EMI: байт прийнято з ACK, у пам'ять ліг зі спотвореним бітом
        --c.glitch_writes;
        c.regs[reg_addr] = static_cast<std::uint8_t>(value ^ 0x02);
        c.desync = true;
        return {};
    }

    // Конфігурація заблокована, поки чип не переведений у Standby
    if (reg_addr >= reg::IntCfg && reg_addr <= reg::IntEnable &&
        (c.regs[reg::Power] & bringup::PowerModeMask) != bringup::PowerStandby) {
        return {};  // ACK є, запису немає — це і ловить Read-Back
    }

    if (reg_addr == reg::Range) {
        c.regs[reg_addr] = static_cast<std::uint8_t>((value & 0x3F) | 0x40);
    } else if (reg_addr == reg::Filter) {
        c.regs[reg_addr] = static_cast<std::uint8_t>(value & 0x7F);
    } else {
        c.regs[reg_addr] = value;
        if (reg_addr == reg::Power) {
            const bool normal =
                (value & bringup::PowerModeMask) == bringup::PowerNormal;
            c.settled_at = normal ? Clock::now() + kSettleTime
                                  : Clock::time_point::max();
        }
    }
    return {};
}

void PowerRail::on() noexcept {
    g_rail_on = true;
    g_sda_low = false;
    g_stuck_clocks = 0;
    for (auto& chip : g_chips) {
        if (chip.mounted) {
            chip_boot(chip, chip.boot);
        }
    }
}

void PowerRail::off() noexcept {
    g_rail_on = false;
    g_sda_low = false;  // зняте живлення заразом відпускає лінію
    g_stuck_clocks = 0;
}

void PowerRail::cycle(std::chrono::milliseconds discharge,
                      std::chrono::milliseconds boot) {
    off();
    sleep(discharge);
    on();
    sleep(boot);
}

GpioTakeover::GpioTakeover() noexcept { g_pins_gpio = true; }
GpioTakeover::~GpioTakeover() { g_pins_gpio = false; }

void GpioTakeover::scl(bool level) noexcept {
    if (!g_pins_gpio) {
        return;
    }
    if (g_scl_level && !level && g_stuck_clocks > 0) {
        // Спад SCL: ведений зсуває наступний біт застряглого байта
        if (--g_stuck_clocks == 0) {
            g_sda_low = false;
        }
    }
    g_scl_level = level;
}

void GpioTakeover::sda(bool) noexcept {}

bool GpioTakeover::sda_is_high() const noexcept { return !g_sda_low; }

bool has_nrst(std::uint8_t dev) noexcept {
    const Chip* chip = find_chip(dev);
    return chip != nullptr && chip->has_nrst;
}

void pulse_nrst(std::uint8_t dev) noexcept {
    Chip* chip = find_chip(dev);
    if (chip == nullptr || !chip->mounted) {
        return;
    }
    g_sda_low = false;
    g_stuck_clocks = 0;
    chip_boot(*chip, chip->boot);
}

void fault_led(bool on) {
    std::println("   [світлодіод несправності {}]", on ? "увімкнено" : "вимкнено");
}

void disable_actuators() { std::println("   [силові приводи знеструмлено]"); }

void sim_reset_board() noexcept {
    g_now_ms = 0;
    g_micros_acc = 0;
    g_rail_on = false;
    g_sda_low = false;
    g_stuck_clocks = 0;
    g_pins_gpio = false;
    g_scl_level = true;
    g_watchdog_kicks = 0;
    g_chips = {};

    // Гіроскоп на місці, NRST розведений; на першу конфігурацію ловить заваду
    g_chips[0] = Chip{.addr = 0x6A, .mounted = true, .has_nrst = true, .boot = 30ms};
    g_chips[0].glitch_writes = 1;

    // Місце давача вологості на цій ревізії плати не запаяне
    g_chips[1] = Chip{.addr = 0x6B, .mounted = false, .has_nrst = false, .boot = 10ms};
}

}  // namespace platform
