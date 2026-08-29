// main.cpp — два однакові чипи на різних шинах під одним драйвером.
//
// Дублювання давача — звичайна вимога до польотного контролера чи блока
// керування батареєю. Драйвер зі станом усередині екземпляра дає це задарма:
// два об'єкти, два транспорти, дві незалежні тіні регістрів.
#include <array>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <format>
#include <iostream>
#include <optional>
#include <span>
#include <string>
#include <vector>

#include "accel/accelerometer.hpp"
#include "accel/linux_i2c.hpp"
#include "accel/reliable_transport.hpp"

namespace {

using Bus = accel::ReliableTransport<accel::LinuxI2cBus>;
using Driver = accel::Accelerometer<Bus>;

volatile std::sig_atomic_t g_stop = 0;

void onInterrupt(int) noexcept
{
    g_stop = 1;
}

// Лінії SCL/SDA для аварійного скидання шини. На платі це виводи
// мікроконтролера, переведені з периферії I2C у звичайний GPIO; у настільному
// прогоні реалізація друкує послідовність тактів і моделює веденого, який
// відпускає SDA після кількох імпульсів, — щоб алгоритм справді виконувався.
class DemoGpioLines {
public:
    explicit DemoGpioLines(unsigned releaseAfter, bool verbose) noexcept
        : releaseAfter_(releaseAfter), verbose_(verbose) {}

    void scl(bool level) noexcept
    {
        if (level) {
            ++pulses_;
            if (pulses_ >= releaseAfter_) {
                sdaLevel_ = true; // ведений виштовхнув останній біт
            }
        }
        if (verbose_) {
            std::cout << std::format("    SCL={} (такт {})\n", level ? 1 : 0, pulses_);
        }
    }

    void sda(bool level) noexcept
    {
        // Відкритий стік: нуль притискає лінію завжди, одиниця лише відпускає
        // її на резистор підтяжки.
        if (!level) {
            sdaLevel_ = false;
        } else if (pulses_ >= releaseAfter_) {
            sdaLevel_ = true;
        }
        if (verbose_) {
            std::cout << std::format("    SDA={}\n", sdaLevel_ ? 1 : 0);
        }
    }

    [[nodiscard]] bool sdaLevel() const noexcept { return sdaLevel_; }

    void delay(std::chrono::microseconds) noexcept
    {
        // На платі тут калібрований цикл або таймер; у настільному прогоні
        // важлива послідовність, а не тривалість.
    }

    void releaseToPeripheral() noexcept
    {
        if (verbose_) {
            std::cout << "    лінії повернуто периферії I2C\n";
        }
    }

private:
    unsigned pulses_{0};
    unsigned releaseAfter_{4};
    bool     sdaLevel_{false}; // ведений тримає лінію — саме звідси зависання
    bool     verbose_{false};
};

static_assert(accel::GpioLines<DemoGpioLines>);

struct Sensor {
    std::string           label;
    std::string           busPath;
    std::uint8_t          address{};
    DemoGpioLines         lines{4, false};
    std::optional<Driver> driver;
};

// Калібрування конкретного екземпляра: зміщення нуля знімають на рівній
// поверхні, підсилення — на поворотному столі.
accel::Calibration benchCalibration()
{
    accel::Calibration calibration;
    calibration.offset = {-12, 8, -35};
    calibration.gain = {1.002F, 0.998F, 1.001F};
    calibration.gainMilli = {0, 0, 0}; // добудує сам драйвер
    return calibration;
}

bool bringUp(Sensor &sensor)
{
    auto bus = accel::LinuxI2cBus::open(sensor.busPath, sensor.address);
    if (!bus) {
        std::cout << std::format("[{}] {} не відкривається\n", sensor.label, sensor.busPath);
        return false;
    }

    sensor.driver.emplace(Bus{std::move(*bus)});

    const Driver::Config config{.range = accel::Range::G4,
                                .odr = accel::Odr::Hz100,
                                .resolution = accel::Resolution::Bits16};

    auto outcome = sensor.driver->initialise(config);
    if (!outcome && outcome.error() == accel::Status::CommFail) {
        std::cout << std::format("  [{}] шина мовчить — пробуємо аварійне скидання\n",
                                 sensor.label);
        sensor.lines = DemoGpioLines{4, true};

        if (auto recovered = sensor.driver->recoverBus(sensor.lines); !recovered) {
            std::cout << std::format("  [{}] скидання не вдалося: {}\n", sensor.label,
                                     accel::describe(recovered.error()));
            sensor.driver.reset();
            return false;
        }
        outcome = sensor.driver->initialise(config);
    }

    if (!outcome) {
        std::cout << std::format("[{}] {} @0x{:02X}: {}\n", sensor.label, sensor.busPath,
                                 sensor.address, accel::describe(outcome.error()));
        sensor.driver.reset();
        return false;
    }

    sensor.driver->setCalibration(benchCalibration());
    std::cout << std::format("[{}] {} @0x{:02X}: готовий, діапазон ±4g, 100 Гц\n",
                             sensor.label, sensor.busPath, sensor.address);
    return true;
}

// Дисципліна 1: чекаємо готовності відліку з жорсткою стелею часу. На платі
// замість очікування стоїть сповіщення з обробника переривання DRDY — але
// транзакцію так само робить задача, а не обробник.
void pollLoop(Sensor &sensor)
{
    constexpr unsigned kFrames = 20;
    std::cout << std::format("\n[{}] збір по готовності відліку ({} кадрів)\n",
                             sensor.label, kFrames);

    for (unsigned frame = 0; frame < kFrames && g_stop == 0; ++frame) {
        if (auto ready = sensor.driver->waitForData(std::chrono::milliseconds{50}); !ready) {
            std::cout << std::format("  кадр {:2}: {}\n", frame, accel::describe(ready.error()));
            if (ready.error() == accel::Status::CommFail) {
                static_cast<void>(sensor.driver->recoverBus(sensor.lines));
            }
            continue;
        }

        const auto raw = sensor.driver->readRaw();
        if (!raw) {
            std::cout << std::format("  кадр {:2}: {}\n", frame, accel::describe(raw.error()));
            continue;
        }

        // Сирий відлік беремо раз: читання очищає прапорець готовності, тож
        // усі три подання рахуються з однієї й тієї ж трійки кодів.
        const accel::Acceleration si = sensor.driver->toSi(*raw);
        const accel::MilliG mg = sensor.driver->toMilliG(*raw);
        const accel::MilliMetrePerSecond2 mm = sensor.driver->toMilliMetrePerSecond2(*raw);
        std::cout << std::format("  кадр {:2}: {:7.3f} {:7.3f} {:7.3f} м/с²  |  "
                                 "{:6} {:6} {:6} мг  |  {:7} {:7} {:7} мм/с²\n",
                                 frame, si.x, si.y, si.z, mg.x, mg.y, mg.z, mm.x, mm.y, mm.z);
    }
}

// Дисципліна 2: чип накопичує відліки сам, процесор спить і забирає пакет.
void fifoLoop(Sensor &sensor)
{
    constexpr std::uint8_t kWatermark = 24;

    const accel::FifoConfig config{.mode = accel::FifoMode::Stream, .watermark = kWatermark};
    if (auto outcome = sensor.driver->configureFifo(config); !outcome) {
        std::cout << std::format("\n[{}] буфер не налаштовано: {}\n", sensor.label,
                                 accel::describe(outcome.error()));
        return;
    }
    static_cast<void>(sensor.driver->enableWatermarkInterrupt(true));

    std::cout << std::format("\n[{}] кільцевий буфер, поріг {} вибірок\n",
                             sensor.label, kWatermark);

    std::array<accel::Acceleration, accel::regs::kFifoDepth> batch{};

    for (unsigned attempt = 0; attempt < 5 && g_stop == 0; ++attempt) {
        const auto status = sensor.driver->fifoStatus();
        if (!status) {
            std::cout << std::format("  стан буфера: {}\n", accel::describe(status.error()));
            break;
        }
        if (status->overrun) {
            std::cout << "  УВАГА: буфер переповнено, частину відліків утрачено\n";
        }
        if (!status->watermarkHit) {
            sensor.driver->transport().delay(std::chrono::milliseconds{100});
            continue;
        }

        const auto count = sensor.driver->readFifo(batch);
        if (!count) {
            std::cout << std::format("  вичитування пакета: {}\n",
                                     accel::describe(count.error()));
            break;
        }

        std::cout << std::format("  забрано {} вибірок, перша Z = {:.3f} м/с², "
                                 "остання Z = {:.3f} м/с²\n",
                                 *count, batch[0].z, batch[*count - 1].z);
        break;
    }

    static_cast<void>(sensor.driver->configureFifo(
        accel::FifoConfig{.mode = accel::FifoMode::Bypass, .watermark = 0}));
    static_cast<void>(sensor.driver->enableWatermarkInterrupt(false));
}

} // namespace

int main(int argc, char **argv)
{
    std::signal(SIGINT, onInterrupt);

    const std::span<char *> args{argv, static_cast<std::size_t>(argc)};

    std::vector<Sensor> sensors;
    sensors.push_back(Sensor{.label = "основний",
                             .busPath = args.size() > 1 ? args[1] : "/dev/i2c-1",
                             .address = 0x19}); // вивід SA0 підтягнуто до живлення
    sensors.push_back(Sensor{.label = "резервний",
                             .busPath = args.size() > 2 ? args[2] : "/dev/i2c-2",
                             .address = 0x18}); // SA0 на землі

    unsigned online = 0;
    for (Sensor &sensor : sensors) {
        if (bringUp(sensor)) {
            ++online;
        }
    }

    if (online == 0) {
        std::cout << "\nЖоден датчик не відповів. Перевірте живлення, підтяжки та адресу SA0.\n";
        return 1;
    }

    for (Sensor &sensor : sensors) {
        if (!sensor.driver) {
            continue;
        }
        pollLoop(sensor);
        fifoLoop(sensor);
        static_cast<void>(sensor.driver->shutdown());
    }

    std::cout << std::format("\nЗавершено. Активних датчиків: {} з {}.\n", online, sensors.size());
    return 0;
}
