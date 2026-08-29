// accelerometer.hpp — драйвер, який перевіряють тести.
//
// Шаблон за типом шини: на платі його інстанціюють транспортом поверх I2C
// периферії, у тесті — моком. Код драйвера при цьому той самий, до байта, —
// інакше тест перевіряв би не те, що поїде в прошивку.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "chip/registers.hpp"
#include "chip/status.hpp"
#include "chip/transport.hpp"

namespace chip {

template <Transport Bus>
class Accelerometer {
public:
    explicit Accelerometer(Bus& bus, RetryPolicy retry = {}) noexcept
        : bus_{&bus}, retry_{retry} {}

    // Перевіряє WHO_AM_I і лише потім конфігурує кремній.
    [[nodiscard]] std::expected<void, Error> init();

    // Змінює діапазон повної шкали, не зачепивши інших бітів CTRL4.
    [[nodiscard]] std::expected<void, Error> setRange(Range range);

    // Один відлік у м/с². NoData, якщо новий вимір ще не готовий.
    [[nodiscard]] std::expected<Sample, Error> readSi();

    // Зупиняє перетворення й повертає конфігурацію з тіньових регістрів.
    [[nodiscard]] std::expected<void, Error> reset();

    [[nodiscard]] bool initialized() const noexcept { return initialized_; }
    [[nodiscard]] Range range() const noexcept { return range_; }

private:
    template <class Operation>
    std::expected<void, Error> withRetries(Operation operation);

    std::expected<std::uint8_t, Error> readRegister(std::uint8_t address);
    std::expected<void, Error> readBlock(std::uint8_t address, std::span<std::uint8_t> out);
    std::expected<void, Error> writeRegister(std::uint8_t address, std::uint8_t value);

    Bus*          bus_;
    RetryPolicy   retry_;
    Range         range_{Range::G2};
    float         scale_{sensitivity(Range::G2)};
    std::uint8_t  shadowCtrl1_{};
    std::uint8_t  shadowCtrl4_{};
    bool          initialized_{false};
};

// --- Транспорт із повторами ------------------------------------------------

// Збій шини сам по собі ще не аварія: на реальній платі це буває від
// наведення чи від зайнятого чипа. Пауза подвоюється, щоб повтори не били
// в шину рівним частоколом.
template <Transport Bus>
template <class Operation>
std::expected<void, Error> Accelerometer<Bus>::withRetries(Operation operation)
{
    auto delay = retry_.baseDelay;
    for (unsigned attempt = 0;; ++attempt) {
        if (auto result = operation(); result) {
            return {};
        }
        if (attempt == retry_.maxRetries) {
            return std::unexpected(Error::Comm);
        }
        bus_->delay(delay);
        delay *= 2;
    }
}

template <Transport Bus>
std::expected<std::uint8_t, Error> Accelerometer<Bus>::readRegister(std::uint8_t address)
{
    std::uint8_t value{};
    auto result = withRetries([&] {
        return bus_->read(address, std::span<std::uint8_t>{&value, 1});
    });
    if (!result) {
        return std::unexpected(result.error());
    }
    return value;
}

template <Transport Bus>
std::expected<void, Error> Accelerometer<Bus>::readBlock(std::uint8_t address,
                                                         std::span<std::uint8_t> out)
{
    // Пакетне читання без біта автоінкременту віддало б шість копій одного
    // байта — саме на цьому спотикається кожен другий перший драйвер.
    const std::uint8_t first = out.size() > 1
                                   ? static_cast<std::uint8_t>(address | reg::AutoIncrement)
                                   : address;
    return withRetries([&] { return bus_->read(first, out); });
}

template <Transport Bus>
std::expected<void, Error> Accelerometer<Bus>::writeRegister(std::uint8_t address,
                                                             std::uint8_t value)
{
    return withRetries([&] {
        return bus_->write(address, std::span<const std::uint8_t>{&value, 1});
    });
}

// --- Життєвий цикл ----------------------------------------------------------

template <Transport Bus>
std::expected<void, Error> Accelerometer<Bus>::init()
{
    initialized_ = false;

    // Поки не доведено, що на шині наш чип, у нього не летить жодного байта
    // конфігурації: писати маски навмання в чужий кремній — найкоротший
    // шлях перевести сусідній пристрій у стан, з якого його дістають лише
    // зняттям живлення.
    auto who = readRegister(reg::WhoAmI);
    if (!who) {
        return std::unexpected(who.error());
    }
    if (*who != reg::WhoAmIValue) {
        return std::unexpected(Error::DeviceNotFound);
    }

    const auto ctrl1 = static_cast<std::uint8_t>((reg::Odr100Hz << reg::Ctrl1OdrShift) |
                                                 reg::Ctrl1AxesMask);
    if (auto written = writeRegister(reg::Ctrl1, ctrl1); !written) {
        return written;
    }

    // BDU не дає кремнію підмінити старший байт, поки ми читаємо молодший;
    // HighRes вмикає повні шістнадцять біт.
    const auto ctrl4 = static_cast<std::uint8_t>(
        reg::Ctrl4Bdu | reg::Ctrl4HighRes |
        (static_cast<std::uint8_t>(Range::G2) << reg::Ctrl4FsShift));
    if (auto written = writeRegister(reg::Ctrl4, ctrl4); !written) {
        return written;
    }

    shadowCtrl1_ = ctrl1;
    shadowCtrl4_ = ctrl4;
    range_       = Range::G2;
    scale_       = sensitivity(Range::G2);
    initialized_ = true;
    return {};
}

template <Transport Bus>
std::expected<void, Error> Accelerometer<Bus>::setRange(Range range)
{
    if (!initialized_) {
        return std::unexpected(Error::NotInitialized);
    }

    // Читання-модифікація-запис іде з тіні в ОЗП: зайва транзакція читання
    // коштувала б часу, а її збій затер би сусідні біти регістра сміттям.
    const auto ctrl4 = static_cast<std::uint8_t>(
        (shadowCtrl4_ & static_cast<std::uint8_t>(~reg::Ctrl4FsMask)) |
        (static_cast<std::uint8_t>(range) << reg::Ctrl4FsShift));

    if (auto written = writeRegister(reg::Ctrl4, ctrl4); !written) {
        return written; // тінь не чіпаємо: у кремнії лишився старий діапазон
    }

    shadowCtrl4_ = ctrl4;
    range_       = range;
    scale_       = sensitivity(range);
    return {};
}

template <Transport Bus>
std::expected<Sample, Error> Accelerometer<Bus>::readSi()
{
    if (!initialized_) {
        return std::unexpected(Error::NotInitialized);
    }

    auto status = readRegister(reg::Status);
    if (!status) {
        return std::unexpected(status.error());
    }
    if ((*status & reg::StatusZyxda) == 0) {
        return std::unexpected(Error::NoData); // старий відлік не віддаємо
    }

    std::array<std::uint8_t, 6> raw{};
    if (auto read = readBlock(reg::OutXL, raw); !read) {
        return std::unexpected(read.error());
    }

    // Молодший байт першим; знак розширюється сам, щойно пара байтів
    // складена в int16_t.
    const auto axis = [&raw](std::size_t index) {
        const auto word = static_cast<std::uint16_t>(
            static_cast<std::uint16_t>(raw[index * 2 + 1] << 8) | raw[index * 2]);
        return static_cast<std::int16_t>(word);
    };

    return Sample{static_cast<float>(axis(0)) * scale_,
                  static_cast<float>(axis(1)) * scale_,
                  static_cast<float>(axis(2)) * scale_};
}

template <Transport Bus>
std::expected<void, Error> Accelerometer<Bus>::reset()
{
    if (!initialized_) {
        return std::unexpected(Error::NotInitialized);
    }

    if (auto stopped = writeRegister(
            reg::Ctrl1, static_cast<std::uint8_t>(reg::OdrPowerDown << reg::Ctrl1OdrShift));
        !stopped) {
        return stopped;
    }
    bus_->delay(std::chrono::milliseconds{5});

    // Після відновлення кремній мусить прокинутись у тому самому режимі,
    // у якому його бачить решта прошивки, — звідси тіньові копії.
    if (auto restored = writeRegister(reg::Ctrl4, shadowCtrl4_); !restored) {
        return restored;
    }
    return writeRegister(reg::Ctrl1, shadowCtrl1_);
}

} // namespace chip
