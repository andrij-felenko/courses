/*
 * Перевірка драйвера на еталонному векторі Bosch і повний цикл читання
 * через імітований датчик на шині.
 */

#include "bmp280.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <format>
#include <iostream>
#include <span>
#include <string_view>

namespace {

using namespace bmp280;

// Еталонні коефіцієнти, спаковані little-endian, як їх віддає OTP.
constexpr std::array<std::uint8_t, calibration_bytes> kCalibBytes{
    0x70, 0x6B, // dig_T1 = 27504
    0x43, 0x67, // dig_T2 = 26435
    0x18, 0xFC, // dig_T3 = -1000
    0x7D, 0x8E, // dig_P1 = 36477
    0x43, 0xD6, // dig_P2 = -10685
    0xD0, 0x0B, // dig_P3 = 3024
    0x27, 0x0B, // dig_P4 = 2855
    0x8C, 0x00, // dig_P5 = 140
    0xF9, 0xFF, // dig_P6 = -7
    0x8C, 0x3C, // dig_P7 = 15500
    0xF8, 0xC6, // dig_P8 = -14600
    0x70, 0x17  // dig_P9 = 6000
};

// adc_P = 0x655AC = 415148, adc_T = 0x7EE90 = 519888
constexpr std::array<std::uint8_t, frame_bytes> kFrameBytes{
    0x65, 0x5A, 0xC0,
    0x7E, 0xE9, 0x00
};

constexpr std::int32_t  kRefTFine    = 128422;
constexpr std::int32_t  kRefTempC100 = 2508;
constexpr std::uint32_t kRefPressure = 100653;

// Імітований датчик: карта регістрів плюс модель зайнятості АЦП.
class FakeSensor {
public:
    FakeSensor() noexcept { power_on_reset(); }

    bool read(std::uint8_t reg_addr, std::span<std::uint8_t> dst) noexcept
    {
        if (static_cast<std::size_t>(reg_addr) + dst.size() > regs_.size()) {
            return false; // вихід за карту — те саме, що NACK на шині
        }

        if (reg_addr == reg::status) {
            std::uint8_t st = 0;
            if (busy_ticks_ > 0) {
                st |= status_measuring;
                --busy_ticks_;
            }
            if (im_update_) {
                st |= status_im_update;
                im_update_ = false;
            }
            regs_[reg::status] = st;
        }

        std::copy_n(regs_.begin() + reg_addr, dst.size(), dst.begin());
        return true;
    }

    bool write(std::uint8_t reg_addr, std::uint8_t value) noexcept
    {
        if (reg_addr == reg::reset) {
            if (value != reset_key) {
                return false; // чужий ключ датчик просто ігнорує
            }
            power_on_reset();
            return true;
        }

        regs_[reg_addr] = value;

        if (reg_addr == reg::ctrl_meas &&
            (value & 0x03u) != static_cast<unsigned>(Mode::sleep)) {
            // Запуск перетворення: за два опитування статусу з'явиться кадр.
            busy_ticks_ = 2;
            std::copy(kFrameBytes.begin(), kFrameBytes.end(),
                      regs_.begin() + reg::data_start);
        }
        return true;
    }

    void delay(std::chrono::milliseconds pause) noexcept
    {
        // Час на хості не йде — вважаємо, що мілісекунда з'їдає такт АЦП.
        busy_ticks_ = std::max<int>(0, busy_ticks_ - static_cast<int>(pause.count()));
    }

private:
    void power_on_reset() noexcept
    {
        regs_.fill(0);
        regs_[reg::id] = chip_id;
        std::copy(kCalibBytes.begin(), kCalibBytes.end(),
                  regs_.begin() + reg::calib_start);

        // Після скидання дані ще порожні: 0x80000 в обох полях.
        regs_[reg::data_start + 0] = 0x80;
        regs_[reg::data_start + 3] = 0x80;

        busy_ticks_ = 0;
        im_update_  = true; // перше читання застає копіювання OTP
    }

    std::array<std::uint8_t, 256> regs_{};
    int  busy_ticks_{0};
    bool im_update_{true};
};

static_assert(RegisterBus<FakeSensor>);

constexpr std::string_view error_name(Error e) noexcept
{
    switch (e) {
        case Error::bus:                    return "шина";
        case Error::wrong_chip:             return "чужий чип";
        case Error::bad_calibration:        return "побите калібрування";
        case Error::timeout:                return "тайм-аут";
        case Error::no_measurement:         return "даних ще немає";
        case Error::degenerate_calibration: return "вироджений поліном";
    }
    return "невідомо";
}

int check_reference_vector()
{
    int failures = 0;

    const auto calib = parse_calibration(std::span<const std::uint8_t, calibration_bytes>{kCalibBytes});
    if (!calib) {
        std::cout << std::format("ПОМИЛКА: калібрування — {}\n", error_name(calib.error()));
        return 1;
    }
    if (calib->dig_T1 != 27504 || calib->dig_T2 != 26435 || calib->dig_T3 != -1000 ||
        calib->dig_P1 != 36477 || calib->dig_P2 != -10685 || calib->dig_P9 != 6000) {
        std::cout << "ПОМИЛКА: коефіцієнти розібрані невірно\n";
        ++failures;
    }

    const auto sample = unpack_frame(std::span<const std::uint8_t, frame_bytes>{kFrameBytes});
    if (!sample) {
        std::cout << std::format("ПОМИЛКА: кадр — {}\n", error_name(sample.error()));
        return failures + 1;
    }
    if (sample->pressure != 415148 || sample->temperature != 519888) {
        std::cout << std::format("ПОМИЛКА: сирі відліки {} / {} замість 415148 / 519888\n",
                                 sample->pressure, sample->temperature);
        ++failures;
    }

    Compensator comp{*calib};
    const auto result = comp.apply(*sample);
    if (!result) {
        std::cout << std::format("ПОМИЛКА: компенсація — {}\n", error_name(result.error()));
        return failures + 1;
    }
    if (result->t_fine != kRefTFine ||
        result->temperature_centi_c != kRefTempC100 ||
        result->pressure_pa() != kRefPressure) {
        std::cout << std::format("ПОМИЛКА: {} / {} / {} замість {} / {} / {}\n",
                                 result->t_fine, result->temperature_centi_c,
                                 result->pressure_pa(),
                                 kRefTFine, kRefTempC100, kRefPressure);
        ++failures;
    }

    std::cout << std::format("Еталон: T = {}.{:02} °C, t_fine = {}, p = {}.{:02} Па\n",
                             result->temperature_centi_c / 100,
                             result->temperature_centi_c % 100,
                             result->t_fine,
                             result->pressure_pa(),
                             (result->pressure_q24_8 & 0xFFu) * 100u / 256u);
    return failures;
}

int check_full_cycle()
{
    FakeSensor sensor;
    const Config cfg{
        .temperature = Oversampling::x2,  // ×2 вистачає для t_fine
        .pressure    = Oversampling::x16, // максимум усереднення, шум 0.16 Па
        .filter      = Filter::x4,        // IIR ×4 проти протягів і струменів
        .standby     = Standby::ms125,
        .mode        = Mode::normal
    };

    auto device = Device<FakeSensor>::open(sensor, cfg);
    if (!device) {
        std::cout << std::format("ПОМИЛКА: відкриття — {}\n", error_name(device.error()));
        return 1;
    }
    std::cout << std::format("Час перетворення: {} мс\n", measurement_time(cfg).count());

    const auto meas = device->read();
    if (!meas) {
        std::cout << std::format("ПОМИЛКА: читання — {}\n", error_name(meas.error()));
        return 1;
    }
    if (meas->temperature_centi_c != kRefTempC100 || meas->pressure_pa() != kRefPressure) {
        std::cout << std::format("ПОМИЛКА: повний цикл дав {} / {}\n",
                                 meas->temperature_centi_c, meas->pressure_pa());
        return 1;
    }

    std::cout << std::format("Повний цикл: T = {}.{:02} °C, p = {} Па\n",
                             meas->temperature_centi_c / 100,
                             meas->temperature_centi_c % 100,
                             meas->pressure_pa());
    return 0;
}

int check_broken_calibration()
{
    std::array<std::uint8_t, calibration_bytes> buf{};

    buf.fill(0xFF);
    if (parse_calibration(std::span<const std::uint8_t, calibration_bytes>{buf})) {
        std::cout << "ПОМИЛКА: обрив шини не розпізнано\n";
        return 1;
    }

    buf.fill(0x00);
    if (parse_calibration(std::span<const std::uint8_t, calibration_bytes>{buf})) {
        std::cout << "ПОМИЛКА: нульове калібрування прийнято\n";
        return 1;
    }
    return 0;
}

} // namespace

int main()
{
    const int failures = check_reference_vector() +
                         check_full_cycle() +
                         check_broken_calibration();

    if (failures != 0) {
        std::cout << std::format("Провалено перевірок: {}\n", failures);
        return 1;
    }
    std::cout << "Драйвер збігається з еталоном біт-у-біт\n";
    return 0;
}
