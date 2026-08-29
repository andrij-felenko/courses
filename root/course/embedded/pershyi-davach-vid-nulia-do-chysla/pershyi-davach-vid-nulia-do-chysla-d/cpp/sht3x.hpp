#pragma once

/* Драйвер SHT3x. Шина задається параметром шаблона: будь-який тип із
   парою write/read над std::span підходить, віртуальних викликів немає.
   Помилка повертається std::expected — прогледіти її неможливо. */

#include <array>
#include <chrono>
#include <concepts>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>
#include <thread>

#include "crc8.hpp"

namespace sht3x {

// Адреса задається виводом ADDR і живе в об'єкті шини.
inline constexpr std::uint8_t kAddrGnd = 0x44;
inline constexpr std::uint8_t kAddrVdd = 0x45;

template <typename T>
concept I2cBus = requires(T& bus, std::span<const std::uint8_t> tx, std::span<std::uint8_t> rx) {
    { bus.write(tx) } -> std::same_as<bool>;
    { bus.read(rx) } -> std::same_as<bool>;
};

enum class Error : std::uint8_t {
    NoDevice,        // чип мовчить на своїй адресі після POR
    I2cWrite,        // команда не отримала ACK
    I2cRead,         // кадр результату не прийшов
    TemperatureCrc,  // спотворене слово температури
    HumidityCrc,     // спотворене слово вологості
    StatusCrc        // спотворене слово регістра стану
};

[[nodiscard]] constexpr std::string_view to_string(Error e) noexcept
{
    switch (e) {
        case Error::NoDevice:       return "чип не відповідає";
        case Error::I2cWrite:       return "збій запису I2C";
        case Error::I2cRead:        return "збій читання I2C";
        case Error::TemperatureCrc: return "CRC температури";
        case Error::HumidityCrc:    return "CRC вологості";
        case Error::StatusCrc:      return "CRC регістра стану";
    }
    return "невідома помилка";
}

enum class Repeatability : std::uint8_t { High, Medium, Low };

struct Reading {
    std::uint16_t raw_temperature{};
    std::uint16_t raw_humidity{};
    std::int32_t  temperature_mc{};  // міліградуси Цельсія
    std::uint32_t humidity_cpm{};    // соті частки відсотка RH

    [[nodiscard]] constexpr float celsius() const noexcept
    {
        return -45.0F + 175.0F * (static_cast<float>(raw_temperature) / 65535.0F);
    }

    [[nodiscard]] constexpr float humidity() const noexcept
    {
        return 100.0F * (static_cast<float>(raw_humidity) / 65535.0F);
    }
};

template <I2cBus Bus>
class Sensor {
public:
    explicit Sensor(Bus& bus) noexcept : bus_(bus) {}

    // Пауза POR плюс перевірка, що чип узагалі відгукується.
    [[nodiscard]] std::expected<void, Error> init()
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(5));

        auto probe = status();
        if (!probe) {
            const Error e = probe.error();
            if (e == Error::I2cWrite || e == Error::I2cRead) {
                return std::unexpected(Error::NoDevice);
            }
            return std::unexpected(e);
        }
        return {};
    }

    [[nodiscard]] std::expected<Reading, Error> measure(Repeatability rep = Repeatability::High)
    {
        const Profile p = profile(rep);

        if (auto sent = send(p.command); !sent) {
            return std::unexpected(sent.error());
        }
        std::this_thread::sleep_for(p.duration);

        std::array<std::uint8_t, 6> rx{};
        if (!bus_.read(rx)) {
            ++bus_errors_;
            return std::unexpected(Error::I2cRead);
        }

        // Хибна сума — відкидаємо ВЕСЬ кадр: завада псує будь-який його біт.
        if (crc8(std::span{rx}.subspan<0, 2>()) != rx[2]) {
            ++crc_errors_;
            return std::unexpected(Error::TemperatureCrc);
        }
        if (crc8(std::span{rx}.subspan<3, 2>()) != rx[5]) {
            ++crc_errors_;
            return std::unexpected(Error::HumidityCrc);
        }
        return decode(rx);
    }

    // Одиночна завада не має валити прилад; пауза між спробами — 30 мс.
    [[nodiscard]] std::expected<Reading, Error> measure_with_retry(
        Repeatability rep = Repeatability::High, int attempts = 3)
    {
        std::expected<Reading, Error> result = std::unexpected(Error::I2cRead);

        for (int i = 0; i < attempts; ++i) {
            if (i > 0) {
                std::this_thread::sleep_for(std::chrono::milliseconds(30));
            }
            result = measure(rep);
            if (result) {
                return result;
            }
        }
        return result;
    }

    // Вбудований нагрівач ~33 мВт: сушить конденсат і служить самоперевіркою.
    [[nodiscard]] std::expected<void, Error> heater(bool on)
    {
        return send(on ? kCmdHeaterOn : kCmdHeaterOff);
    }

    [[nodiscard]] std::expected<std::uint16_t, Error> status()
    {
        if (auto sent = send(kCmdStatus); !sent) {
            return std::unexpected(sent.error());
        }

        std::array<std::uint8_t, 3> rx{};
        if (!bus_.read(rx)) {
            ++bus_errors_;
            return std::unexpected(Error::I2cRead);
        }
        if (crc8(std::span{rx}.subspan<0, 2>()) != rx[2]) {
            ++crc_errors_;
            return std::unexpected(Error::StatusCrc);
        }
        return static_cast<std::uint16_t>((rx[0] << 8) | rx[1]);
    }

    [[nodiscard]] std::uint32_t bus_errors() const noexcept { return bus_errors_; }
    [[nodiscard]] std::uint32_t crc_errors() const noexcept { return crc_errors_; }

private:
    struct Profile {
        std::uint16_t             command;
        std::chrono::milliseconds duration;
    };

    // Режим без утримання SCL: паузу відлічує господар шини.
    // До верхньої межі t_meas додано 1 мс — інакше буде NACK.
    [[nodiscard]] static constexpr Profile profile(Repeatability rep) noexcept
    {
        using std::chrono::milliseconds;
        switch (rep) {
            case Repeatability::Medium: return {0x240B, milliseconds{7}};
            case Repeatability::Low:    return {0x2416, milliseconds{5}};
            case Repeatability::High:   break;
        }
        return {0x2400, milliseconds{16}};
    }

    [[nodiscard]] std::expected<void, Error> send(std::uint16_t command)
    {
        const std::array<std::uint8_t, 2> tx{static_cast<std::uint8_t>(command >> 8),
                                             static_cast<std::uint8_t>(command & 0xFF)};
        if (!bus_.write(tx)) {
            ++bus_errors_;
            return std::unexpected(Error::I2cWrite);
        }
        return {};
    }

    [[nodiscard]] static constexpr Reading decode(std::span<const std::uint8_t, 6> rx) noexcept
    {
        const auto raw_t  = static_cast<std::uint16_t>((rx[0] << 8) | rx[1]);
        const auto raw_rh = static_cast<std::uint16_t>((rx[3] << 8) | rx[4]);

        // 175000/65535 скорочено на 5 до 35000/13107, тож найбільший
        // проміжний добуток 35000 * 65535 ще вміщається в 32 біти —
        // ані int64, ані плаваючої коми на дрібному ядрі не потрібно.
        return Reading{
            .raw_temperature = raw_t,
            .raw_humidity    = raw_rh,
            .temperature_mc  = -45000 + static_cast<std::int32_t>((35000U * raw_t) / 13107U),
            .humidity_cpm    = (10000U * static_cast<std::uint32_t>(raw_rh)) / 65535U,
        };
    }

    static constexpr std::uint16_t kCmdStatus     = 0xF32D;
    static constexpr std::uint16_t kCmdHeaterOn   = 0x306D;
    static constexpr std::uint16_t kCmdHeaterOff  = 0x3066;

    Bus&          bus_;
    std::uint32_t bus_errors_{};
    std::uint32_t crc_errors_{};
};

}  // namespace sht3x
