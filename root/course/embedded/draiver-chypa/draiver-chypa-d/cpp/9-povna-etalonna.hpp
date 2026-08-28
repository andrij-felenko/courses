// ============================================================================
// C++20: Ідіоматичний типізований драйвер акселерометра
// ============================================================================
#pragma once

#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <concepts>

namespace embedded::sensors {

enum class Status : std::int32_t {
    Ok           =  0,
    InvalidParam = -1,
    CommFail     = -2,
    Timeout      = -3,
    NotFound     = -4,
    NotInit      = -5,
    NoData       = -6
};

enum class Range : std::uint8_t {
    G2  = 0, // ±2g
    G4  = 1, // ±4g
    G8  = 2, // ±8g
    G16 = 3  // ±16g
};

struct AccelerationSi {
    float x{0.0F}; // м/с²
    float y{0.0F}; // м/с²
    float z{0.0F}; // м/с²
};

// Концепт для шинного транспорту
template <typename T>
concept BusTransport = requires(T transport, std::uint8_t reg, std::span<std::uint8_t> rx, std::span<const std::uint8_t> tx) {
    { transport.read(reg, rx) } -> std::same_as<Status>;
    { transport.write(reg, tx) } -> std::same_as<Status>;
    { transport.delay_ms(std::uint32_t{}) } -> std::same_as<void>;
};

template <BusTransport Transport>
class AccelerometerDriver {
public:
    static constexpr std::uint8_t RegWhoAmI     = 0x0F;
    static constexpr std::uint8_t RegCtrl1      = 0x20;
    static constexpr std::uint8_t RegCtrl4      = 0x23;
    static constexpr std::uint8_t RegStatus     = 0x27;
    static constexpr std::uint8_t RegOutXL      = 0x28;

    static constexpr std::uint8_t ExpectedId    = 0x33;
    static constexpr std::uint8_t AutoIncrement = 0x80;
    static constexpr float StandardGravity      = 9.80665F;

    explicit constexpr AccelerometerDriver(Transport transport, std::uint8_t address = 0x19) noexcept
        : transport_(transport), address_(address) {}

    [[nodiscard]] Status init() noexcept {
        transport_.delay_ms(10);

        // Крок 1: Зчитування та перевірка WHO_AM_I
        std::array<std::uint8_t, 1> chip_id{0};
        if (auto res = transport_.read(RegWhoAmI, chip_id); res != Status::Ok) {
            return res;
        }
        if (chip_id[0] != ExpectedId) {
            return Status::NotFound;
        }

        // Крок 2: Конфігурація BDU та діапазону (CTRL_REG4)
        range_ = Range::G2;
        scale_factor_ = calculateScaleFactor(range_);
        shadow_ctrl4_ = 0x80U | (static_cast<std::uint8_t>(range_) << 4); // BDU enabled

        std::array<const std::uint8_t, 1> tx_ctrl4{shadow_ctrl4_};
        if (auto res = transport_.write(RegCtrl4, tx_ctrl4); res != Status::Ok) {
            return res;
        }

        // Крок 3: Увімкнення 100 Гц та 3 осей (CTRL_REG1)
        shadow_ctrl1_ = 0x57U; // 100 Hz, X/Y/Z enabled
        std::array<const std::uint8_t, 1> tx_ctrl1{shadow_ctrl1_};
        if (auto res = transport_.write(RegCtrl1, tx_ctrl1); res != Status::Ok) {
            return res;
        }

        is_initialized_ = true;
        return Status::Ok;
    }

    [[nodiscard]] Status setRange(Range range) noexcept {
        if (!is_initialized_) return Status::NotInit;

        shadow_ctrl4_ = static_cast<std::uint8_t>((shadow_ctrl4_ & ~0x30U) | (static_cast<std::uint8_t>(range) << 4));
        std::array<const std::uint8_t, 1> tx{shadow_ctrl4_};
        if (auto res = transport_.write(RegCtrl4, tx); res != Status::Ok) {
            return res;
        }

        range_ = range;
        scale_factor_ = calculateScaleFactor(range);
        return Status::Ok;
    }

    [[nodiscard]] std::expected<AccelerationSi, Status> readAccelerationSi() noexcept {
        if (!is_initialized_) return std::unexpected(Status::NotInit);

        // Перевірка готовності даних
        std::array<std::uint8_t, 1> status{0};
        if (auto res = transport_.read(RegStatus, status); res != Status::Ok) {
            return std::unexpected(res);
        }
        if ((status[0] & 0x08U) == 0) {
            return std::unexpected(Status::NoData);
        }

        // Пакетне читання 6 байтів
        std::array<std::uint8_t, 6> raw_buf{};
        if (auto res = transport_.read(RegOutXL | AutoIncrement, raw_buf); res != Status::Ok) {
            return std::unexpected(res);
        }

        const auto raw_x = static_cast<std::int16_t>(raw_buf[0] | (static_cast<std::uint16_t>(raw_buf[1]) << 8));
        const auto raw_y = static_cast<std::int16_t>(raw_buf[2] | (static_cast<std::uint16_t>(raw_buf[3]) << 8));
        const auto raw_z = static_cast<std::int16_t>(raw_buf[4] | (static_cast<std::uint16_t>(raw_buf[5]) << 8));

        return AccelerationSi{
            .x = static_cast<float>(raw_x) * scale_factor_,
            .y = static_cast<float>(raw_y) * scale_factor_,
            .z = static_cast<float>(raw_z) * scale_factor_
        };
    }

    [[nodiscard]] constexpr bool isInitialized() const noexcept {
        return is_initialized_;
    }

private:
    [[nodiscard]] static constexpr float calculateScaleFactor(Range range) noexcept {
        float mg_per_lsb = 0.061F;
        switch (range) {
            case Range::G2:  mg_per_lsb = 0.061F; break;
            case Range::G4:  mg_per_lsb = 0.122F; break;
            case Range::G8:  mg_per_lsb = 0.244F; break;
            case Range::G16: mg_per_lsb = 0.732F; break;
        }
        return (mg_per_lsb / 1000.0F) * StandardGravity;
    }

    Transport transport_;
    std::uint8_t address_{0x19};
    Range range_{Range::G2};
    float scale_factor_{0.00059820565F};
    std::uint8_t shadow_ctrl1_{0x00};
    std::uint8_t shadow_ctrl4_{0x00};
    bool is_initialized_{false};
};

} // namespace embedded::sensors
