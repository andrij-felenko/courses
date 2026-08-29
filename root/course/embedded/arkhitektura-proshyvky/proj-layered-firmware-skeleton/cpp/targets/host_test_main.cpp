// targets/host_test_main.cpp — стенд для робочої станції розробника.
// Ні мікроконтролера, ні давача: шина, ніжка й годинник підмінені класами-заглушками,
// а бізнес-логіка виконується та сама, байт у байт.
#undef NDEBUG  // Перевірки мають працювати і в збірці з оптимізацією
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <print>

#include "app/app_telemetry.hpp"
#include "bsp/bsp_bme280.hpp"
#include "bsp/power_rail.hpp"
#include "hal/clock.hpp"
#include "hal/hal_gpio.hpp"
#include "hal/hal_i2c.hpp"
#include "services/dispatcher.hpp"
#include "services/event_queue.hpp"
#include "services/power_manager.hpp"

namespace {

using namespace std::chrono_literals;

// ---------------------------------------------------------------------------
// Заглушка шини: масив регістрів плюс кероване псування звʼязку
// ---------------------------------------------------------------------------
class MockI2cBus final : public hal::II2cBus {
public:
    std::expected<void, hal::I2cError> read_reg(std::uint8_t dev_addr, std::uint8_t reg_addr,
                                                std::span<std::uint8_t> data) override
    {
        if (auto guard = check(dev_addr); !guard) {
            return guard;
        }
        ++reads_;
        for (std::size_t i = 0; i < data.size(); ++i) {
            data[i] = registers_[(reg_addr + i) & 0xFFU];
        }
        return {};
    }

    std::expected<void, hal::I2cError> write_reg(std::uint8_t dev_addr, std::uint8_t reg_addr,
                                                 std::span<const std::uint8_t> data) override
    {
        if (auto guard = check(dev_addr); !guard) {
            return guard;
        }
        ++writes_;
        for (std::size_t i = 0; i < data.size(); ++i) {
            registers_[(reg_addr + i) & 0xFFU] = data[i];
        }
        return {};
    }

    void inject_fault(hal::I2cError err) { fault_ = err; }
    void clear_fault() { fault_.reset(); }
    bool faulted() const { return fault_.has_value(); }

    void set_powered(bool on)
    {
        powered_ = on;
        if (!on) {
            // Знеструмлення прибирає завислий стан мікросхеми — заради цього все й затіяно.
            fault_.reset();
        }
    }

    std::uint8_t& reg(std::uint8_t index) { return registers_[index]; }

    std::uint32_t reads() const noexcept { return reads_; }
    std::uint32_t writes() const noexcept { return writes_; }

    void put_u16(std::uint8_t index, std::uint16_t value)
    {
        registers_[index] = static_cast<std::uint8_t>(value & 0xFFU);
        registers_[index + 1U] = static_cast<std::uint8_t>(value >> 8);
    }

private:
    std::expected<void, hal::I2cError> check(std::uint8_t dev_addr) const
    {
        if (dev_addr != bsp::Bme280::kPrimaryAddress) {
            return std::unexpected(hal::I2cError::Nack);
        }
        if (!powered_) {
            return std::unexpected(hal::I2cError::Timeout);  // Знеструмлений давач мовчить
        }
        if (fault_) {
            return std::unexpected(*fault_);
        }
        return {};
    }

    std::array<std::uint8_t, 256> registers_{};
    std::optional<hal::I2cError> fault_{};
    bool powered_{true};
    std::uint32_t reads_{0};
    std::uint32_t writes_{0};
};

// ---------------------------------------------------------------------------
// Заглушка ніжки живлення: клацання ключем «ремонтує» уявний давач
// ---------------------------------------------------------------------------
class MockGpioPin final : public hal::IGpioPin {
public:
    explicit MockGpioPin(MockI2cBus& sensor) noexcept : sensor_(sensor) {}

    std::expected<void, hal::GpioError> write(hal::Level level) override
    {
        if (level_ == hal::Level::High && level == hal::Level::Low) {
            ++falling_edges_;
        }
        sensor_.set_powered(level == hal::Level::High);
        level_ = level;
        return {};
    }

    std::expected<hal::Level, hal::GpioError> read() const override { return level_; }

    std::uint32_t falling_edges() const noexcept { return falling_edges_; }
    hal::Level level() const noexcept { return level_; }

private:
    MockI2cBus& sensor_;
    hal::Level level_{hal::Level::High};
    std::uint32_t falling_edges_{0};
};

// ---------------------------------------------------------------------------
// Заглушка годинника: час рухає сам тест, а не кварц
// ---------------------------------------------------------------------------
class MockClock final : public hal::IClock {
public:
    time_point now() const override { return now_; }
    void sleep_for(duration d) override { now_ += d; }
    void advance(duration d) { now_ += d; }

private:
    time_point now_{0};
};

// ---------------------------------------------------------------------------
// Заповнення уявної мікросхеми: калібрування з довідки Bosch і вибірка на 40 °C
// ---------------------------------------------------------------------------
void load_sensor_image(MockI2cBus& bus)
{
    bus.reg(0xD0) = 0x60;  // Ідентифікатор BME280
    bus.reg(0xF3) = 0x00;  // Вибірка завершена, NVM перенесено

    bus.put_u16(0x88, 27504);                              // dig_T1
    bus.put_u16(0x8A, static_cast<std::uint16_t>(26435));  // dig_T2
    bus.put_u16(0x8C, static_cast<std::uint16_t>(-1000));  // dig_T3
    bus.put_u16(0x8E, 36477);                              // dig_P1
    bus.put_u16(0x90, static_cast<std::uint16_t>(-10685)); // dig_P2
    bus.put_u16(0x92, static_cast<std::uint16_t>(3024));   // dig_P3
    bus.put_u16(0x94, static_cast<std::uint16_t>(2855));   // dig_P4
    bus.put_u16(0x96, static_cast<std::uint16_t>(140));    // dig_P5
    bus.put_u16(0x98, static_cast<std::uint16_t>(-7));     // dig_P6
    bus.put_u16(0x9A, static_cast<std::uint16_t>(15500));  // dig_P7
    bus.put_u16(0x9C, static_cast<std::uint16_t>(-14600)); // dig_P8
    bus.put_u16(0x9E, static_cast<std::uint16_t>(6000));   // dig_P9

    bus.reg(0xA1) = 75;                                   // dig_H1
    bus.put_u16(0xE1, static_cast<std::uint16_t>(350));   // dig_H2
    bus.reg(0xE3) = 0;                                    // dig_H3
    bus.reg(0xE4) = 0x14;                                 // dig_H4, старші 8 біт
    bus.reg(0xE5) = 0x06;                                 // молодший півбайт H4, старший — H5
    bus.reg(0xE6) = 0x00;                                 // dig_H5, старші 8 біт
    bus.reg(0xE7) = 30;                                   // dig_H6

    // Тиск: сирий код АЦП 415148
    bus.reg(0xF7) = 0x65;
    bus.reg(0xF8) = 0x5A;
    bus.reg(0xF9) = 0xC0;
    // Температура: сирий код 567591 → рівно 40.0 °C після компенсації
    bus.reg(0xFA) = 0x8A;
    bus.reg(0xFB) = 0x92;
    bus.reg(0xFC) = 0x70;
    // Вологість: сирий код 31232
    bus.reg(0xFD) = 0x7A;
    bus.reg(0xFE) = 0x00;
}

// ---------------------------------------------------------------------------
// Перехідник відновлення: служба живлення не знає ні про BME280, ні про телеметрію
// ---------------------------------------------------------------------------
class SensorRecovery final : public services::IRecoverable {
public:
    SensorRecovery(bsp::Bme280& sensor, app::TelemetryCoordinator& app) noexcept
        : sensor_(sensor), app_(app)
    {
    }

    bool reinitialize() override { return sensor_.initialize().has_value(); }
    void on_recovered() override { app_.notify_recovered(); }

private:
    bsp::Bme280& sensor_;
    app::TelemetryCoordinator& app_;
};

// ---------------------------------------------------------------------------
// Стенд: усі шари, зібрані так само, як на реальній платі
// ---------------------------------------------------------------------------
using Queue = services::EventQueue<16>;

struct Bench {
    Bench(float threshold_c, std::uint16_t sample_period_ticks)
        : pin(bus),
          sensor(bus, bsp::Bme280::kPrimaryAddress),
          rail(pin, clock, hal::Level::High, 50ms, 100ms),
          sink(queue),
          dispatcher(queue),
          app(sensor, sink, threshold_c, sample_period_ticks),
          recovery(sensor, app),
          power(rail, clock, recovery, 1000ms)
    {
        load_sensor_image(bus);
        assert(sensor.initialize().has_value());
        assert(dispatcher.subscribe(app::TelemetryCoordinator::subscription(), app));
        assert(dispatcher.subscribe(services::PowerManager::subscription(), power));
    }

    void push(services::EventType type)
    {
        assert(queue.push(services::Event{.type = type, .timestamp = clock.now(), .payload = {}}));
    }

    MockI2cBus bus;
    MockClock clock;
    MockGpioPin pin;
    bsp::Bme280 sensor;
    bsp::PowerRail rail;
    Queue queue;
    services::QueueSink<Queue> sink;
    services::Dispatcher<Queue> dispatcher;
    app::TelemetryCoordinator app;
    SensorRecovery recovery;
    services::PowerManager power;
};

// ---------------------------------------------------------------------------
// Перевірка 1: перевищення порога породжує подію тривоги
// ---------------------------------------------------------------------------
void test_alert_above_threshold()
{
    Bench b{35.0F, 10};

    const auto reading = b.sensor.read();
    assert(reading.has_value());
    assert(b.bus.reads() > 0 && b.bus.writes() > 0);  // Ініціалізація справді ходила на шину
    assert(std::fabs(reading->temperature_c - 40.0F) < 0.5F);
    assert(reading->humidity_percent >= 0.0F && reading->humidity_percent <= 100.0F);

    b.push(services::EventType::SensorTrigger);
    assert(b.dispatcher.drain() == 2);  // Тригер плюс породжена тривога

    assert(b.app.samples_taken() == 1);
    assert(b.app.alerts_raised() == 1);
    std::println("  1. тривога: T={:.2f} °C, RH={:.1f} %, p={:.1f} гПа", reading->temperature_c,
                 reading->humidity_percent, reading->pressure_hpa);
}

// ---------------------------------------------------------------------------
// Перевірка 2: під порогом тривоги немає
// ---------------------------------------------------------------------------
void test_no_alert_below_threshold()
{
    Bench b{50.0F, 10};

    b.push(services::EventType::SensorTrigger);
    b.dispatcher.drain();

    assert(b.app.samples_taken() == 1);
    assert(b.app.alerts_raised() == 0);
    std::println("  2. поріг 50 °C: тривоги немає");
}

// ---------------------------------------------------------------------------
// Перевірка 3: період опитування рахується в тиках таймера
// ---------------------------------------------------------------------------
void test_tick_period()
{
    Bench b{35.0F, 10};

    for (int i = 0; i < 9; ++i) {
        b.push(services::EventType::TimerTick);
        b.dispatcher.drain();
    }
    assert(b.app.samples_taken() == 0);

    b.push(services::EventType::TimerTick);
    b.dispatcher.drain();
    assert(b.app.samples_taken() == 1);
    std::println("  3. період: вибірка на десятому тику");
}

// ---------------------------------------------------------------------------
// Перевірка 4: повне трасування збою шини — від таймауту до перезапуску живлення
// ---------------------------------------------------------------------------
void test_bus_fault_recovery()
{
    Bench b{35.0F, 1};

    // Крок 1: лінію SDA притиснуто, HAL віддає таймаут
    b.bus.inject_fault(hal::I2cError::Timeout);

    // Крок 2 і 3: дві невдачі мовчазні, третя переповнює терпіння координатора
    b.push(services::EventType::SensorTrigger);
    b.dispatcher.drain();
    assert(b.app.faults_raised() == 0);

    b.push(services::EventType::SensorTrigger);
    b.dispatcher.drain();
    assert(b.app.faults_raised() == 0);

    const std::uint32_t edges_before = b.pin.falling_edges();
    b.push(services::EventType::SensorTrigger);
    // Крок 4: диспетчер витягує подію несправності й віддає її службі живлення
    b.dispatcher.drain();

    assert(b.app.faults_raised() == 1);
    assert(b.power.cycles_done() == 1);
    assert(b.rail.cycles() == 1);
    assert(b.pin.falling_edges() == edges_before + 1);
    assert(b.pin.level() == hal::Level::High);  // Живлення повернуто
    assert(!b.bus.faulted());                   // Давач відпустив шину
    assert(b.app.consecutive_failures() == 0);

    // Після відновлення вузол знову міряє й знову бачить перевищення порога.
    // Знімаємо рівно одну подію, щоб тривога лишилась у черзі на перевірку.
    b.push(services::EventType::SensorTrigger);
    assert(b.dispatcher.run_once());
    assert(b.app.samples_taken() == 1);

    const auto alert = b.queue.pop();
    assert(alert.has_value());
    assert(alert->type == services::EventType::AlertThreshold);
    const float* temperature = std::get_if<float>(&alert->payload);
    assert(temperature != nullptr);
    assert(std::fabs(*temperature - 40.0F) < 0.5F);
    std::println("  4. збій шини: {} скидання живлення, вузол ожив", b.power.cycles_done());
}

// ---------------------------------------------------------------------------
// Перевірка 5: переповнена черга відкидає подію, а не псує памʼять
// ---------------------------------------------------------------------------
void test_queue_overflow()
{
    Queue q;
    const services::Event evt{.type = services::EventType::TimerTick, .timestamp = 0ms, .payload = {}};

    // Кільце на N комірок вміщає N-1 подію: одна лишається порожньою, щоб
    // «повно» не було не відрізнити від «порожньо».
    for (std::size_t i = 0; i < Queue::capacity() - 1; ++i) {
        assert(q.push(evt));
    }
    assert(!q.push(evt));
    assert(q.dropped() == 1);
    assert(q.size() == Queue::capacity() - 1);

    const auto out = q.pop();
    assert(out.has_value());
    assert(out->type == services::EventType::TimerTick);
    assert(q.push(evt));  // Місце звільнилось
    std::println("  5. переповнення: подію відкинуто, лічильник зріс");
}

}  // namespace

int main()
{
    std::println("Хостовий стенд каркаса прошивки (без мікроконтролера й давача):");
    test_alert_above_threshold();
    test_no_alert_below_threshold();
    test_tick_period();
    test_bus_fault_recovery();
    test_queue_overflow();
    std::println("Усі перевірки пройдено.");
    return 0;
}
