// Фаза 3: шина I2C — розблокування, ініціалізація, сканування адрес.
#include "bringup.hpp"

namespace bringup {
namespace {

namespace i2c = mmio::i2c1;
namespace rcc = mmio::rcc;

constexpr mmio::Pin scl{mmio::portb, 6U};
constexpr mmio::Pin sda{mmio::portb, 7U};

constexpr std::uint32_t bus_speed_hz = 100'000U;
constexpr std::uint32_t bus_clear_half_us = 5U;
constexpr std::uint32_t bus_clear_pulses = 9U;   // байт даних плюс біт ACK
constexpr std::uint32_t event_tries = 20'000U;
constexpr std::uint32_t inter_probe_us = 100U;

void release_line(const mmio::Pin& pin) noexcept
{
    pin.enable_clock();
    pin.write(true);   // спершу відпускаємо лінію, потім вмикаємо вихід
    pin.configure(mmio::Mode::output, mmio::OutputType::open_drain, mmio::Pull::up);
}

void hand_to_peripheral(const mmio::Pin& pin) noexcept
{
    pin.select_alternate(i2c::alternate_function);
    pin.configure(mmio::Mode::alternate, mmio::OutputType::open_drain, mmio::Pull::up);
}

// Ручне розблокування шини: ведений, перерваний посеред байта, тактується
// тільки від SCL і сам лінію не відпустить.
[[nodiscard]] Result<bool> clear_stuck_bus() noexcept
{
    i2c::cr1::clear(i2c::pe);   // поки модуль увімкнений, виводи належать йому

    release_line(scl);
    release_line(sda);
    mmio::delay_us(bus_clear_half_us);

    const bool was_stuck = !sda.read();
    if (!was_stuck) {
        hand_to_peripheral(scl);
        hand_to_peripheral(sda);
        return false;
    }

    for (std::uint32_t pulse = 0U; pulse < bus_clear_pulses && !sda.read(); ++pulse) {
        scl.write(false);
        mmio::delay_us(bus_clear_half_us);
        scl.write(true);
        mmio::delay_us(bus_clear_half_us);
    }

    if (!sda.read()) {
        // Повний байт тактів не допоміг: це вже не зависла транзакція, а
        // закорочена доріжка або мертвий ведений.
        hand_to_peripheral(scl);
        hand_to_peripheral(sda);
        return std::unexpected(Error::i2c_bus_stuck);
    }

    // Коректна умова STOP: SDA переходить 0 → 1 при високому SCL.
    scl.write(false);
    sda.write(false);
    mmio::delay_us(bus_clear_half_us);
    scl.write(true);
    mmio::delay_us(bus_clear_half_us);
    sda.write(true);
    mmio::delay_us(bus_clear_half_us);

    hand_to_peripheral(scl);
    hand_to_peripheral(sda);
    return true;
}

void configure_peripheral(std::uint32_t pclk_hz) noexcept
{
    rcc::apb1enr::set(rcc::i2c1en);
    static_cast<void>(rcc::apb1enr::read());

    // Після зависання шини модуль лишається у стані BUSY, і зняти його
    // можна тільки програмним скиданням.
    i2c::cr1::write(i2c::swrst);
    i2c::cr1::write(0U);

    const std::uint32_t pclk_mhz = pclk_hz / 1'000'000U;
    std::uint32_t ccr_value = pclk_hz / (2U * bus_speed_hz);
    if (ccr_value < 4U) {
        ccr_value = 4U;   // межа стандартного режиму
    }

    i2c::cr2::write(pclk_mhz);          // модуль має знати частоту APB1
    i2c::ccr::write(ccr_value);         // Sm: половина періоду в тактах APB1
    i2c::trise::write(pclk_mhz + 1U);   // максимальний фронт 1000 нс
    i2c::cr1::set(i2c::pe);
}

// Умову STOP треба виставити на КОЖНОМУ виході з проби — і на успіху, і на
// NACK, і на таймауті. У C це мітка `out`, тут — деструктор.
struct StopGuard {
    ~StopGuard() noexcept { i2c::cr1::set(i2c::stop); }
};

}  // namespace

Result<I2cBus> I2cBus::open(std::uint32_t pclk_hz) noexcept
{
    auto stuck = clear_stuck_bus();
    if (!stuck) {
        return std::unexpected(stuck.error());
    }
    configure_peripheral(pclk_hz);
    return I2cBus{*stuck};
}

I2cBus::I2cBus(I2cBus&& other) noexcept
    : bus_was_stuck_{other.bus_was_stuck_}, owns_peripheral_{other.owns_peripheral_}
{
    other.owns_peripheral_ = false;
}

I2cBus& I2cBus::operator=(I2cBus&& other) noexcept
{
    if (this != &other) {
        release();
        bus_was_stuck_ = other.bus_was_stuck_;
        owns_peripheral_ = other.owns_peripheral_;
        other.owns_peripheral_ = false;
    }
    return *this;
}

I2cBus::~I2cBus() noexcept
{
    release();
}

void I2cBus::release() noexcept
{
    if (owns_peripheral_) {
        i2c::cr1::clear(i2c::pe);   // модуль відпускає лінії підтяжкам
        owns_peripheral_ = false;
    }
}

Result<void> I2cBus::probe(std::uint8_t address_7bit) noexcept
{
    // Шина мусить бути вільна, інакше START не піде взагалі.
    if (!mmio::wait_until([] { return !i2c::sr2::any(i2c::flag_busy); }, event_tries)) {
        return std::unexpected(Error::i2c_timeout);
    }

    i2c::cr1::set(i2c::start);
    StopGuard stop_on_exit;

    if (!mmio::wait_until([] { return i2c::sr1::any(i2c::flag_sb); }, event_tries)) {
        return std::unexpected(Error::i2c_timeout);
    }

    // SB знімається читанням SR1 із наступним записом у DR.
    static_cast<void>(i2c::sr1::read());
    i2c::dr::write(static_cast<std::uint32_t>(address_7bit) << 1);   // напрямок: запис

    static_cast<void>(mmio::wait_until(
        [] { return i2c::sr1::any(i2c::flag_addr | i2c::flag_af); }, event_tries));

    const std::uint32_t sr1 = i2c::sr1::read();
    if ((sr1 & i2c::flag_af) != 0U) {
        // NACK: на дев'ятому такті ніхто не притиснув SDA до землі.
        i2c::sr1::clear(i2c::flag_af);
        return std::unexpected(Error::i2c_nack);
    }
    if ((sr1 & i2c::flag_addr) == 0U) {
        return std::unexpected(Error::i2c_timeout);
    }

    static_cast<void>(i2c::sr2::read());   // ADDR знімається парою SR1 + SR2
    return {};
}

Result<std::size_t> I2cBus::scan(std::span<std::uint8_t> found) noexcept
{
    std::size_t count = 0U;

    for (std::uint32_t address = first_address; address <= last_address; ++address) {
        const auto result = probe(static_cast<std::uint8_t>(address));
        if (result) {
            if (count < found.size()) {
                found[count] = static_cast<std::uint8_t>(address);
            }
            ++count;
        } else if (result.error() == Error::i2c_timeout) {
            // Модуль застряг — перебирати решту адрес немає сенсу.
            return std::unexpected(Error::i2c_timeout);
        }
        mmio::delay_us(inter_probe_us);
    }

    if (count == 0U) {
        return std::unexpected(Error::i2c_nack);
    }
    return count;
}

}  // namespace bringup
