/*
 * Модульні тести адаптера на хості. Замість чипа — клас, що реалізує
 * той самий інтерфейс II2cBus і за командою ламається.
 *
 * Збірка з кореня проєкту:
 *   cc  -std=c11 -c vendor/vendor_sensor.c -o vendor_sensor.o
 *   c++ -std=c++23 -I include -I . -Wall -Wextra -o test_adapter \
 *       tests/test_adapter.cpp src/adapter.cpp vendor_sensor.o
 */
#include "sensor/adapter.hpp"
#include "sensor/i2c_bus.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <optional>
#include <span>
#include <utility>

namespace {

constexpr std::uint8_t kCalib00 = 0x88;
constexpr std::uint8_t kChipId = 0xD0;
constexpr std::uint8_t kReset = 0xE0;
constexpr std::uint8_t kStatus = 0xF3;
constexpr std::uint8_t kCtrlMeas = 0xF4;
constexpr std::uint8_t kPressMsb = 0xF7;

/* Програмний емулятор кремнію з керованими відмовами. */
class MockChip final : public sensor::II2cBus {
public:
    MockChip()
    {
        load_factory();
        reset();
    }

    /* Прапорці генерації апаратних збоїв. */
    bool nack_all{false};
    std::optional<std::uint8_t> fail_reg{};   /* обрив на конкретному пакеті */
    bool stuck_measuring{false};              /* перетворення не завершується */

    std::uint32_t reads{0};
    std::uint32_t writes{0};

    /* Заводський образ, а не робочий регістр: м'яке скидання, з якого
       починає драйвер, перезаллє регістри саме звідси. */
    void poke(std::uint8_t addr, std::uint8_t value) { nvm_[addr] = value; }

    void put_u16(std::uint8_t addr, std::uint16_t value)
    {
        nvm_[addr] = static_cast<std::uint8_t>(value & 0xFFU);
        nvm_[static_cast<std::uint8_t>(addr + 1)] =
            static_cast<std::uint8_t>(value >> 8);
    }

    bool read_registers(std::uint8_t, std::uint8_t reg,
                        std::span<std::uint8_t> buffer) override
    {
        if (nack_all || (fail_reg && *fail_reg == reg)) {
            return false;
        }
        ++reads;

        if (reg == kStatus && buffer.size() == 1U) {
            std::uint8_t status = 0U;
            if (im_update_left_ > 0U) {
                --im_update_left_;
                status |= 0x01U;
            }
            if (stuck_measuring) {
                status |= 0x08U;
            } else if (measuring_left_ > 0U) {
                --measuring_left_;
                status |= 0x08U;
            }
            buffer[0] = status;
            return true;
        }

        for (std::size_t i = 0; i < buffer.size(); ++i) {
            buffer[i] = regs_[static_cast<std::uint8_t>(reg + i)];
        }
        return true;
    }

    bool write_registers(std::uint8_t, std::uint8_t reg,
                         std::span<const std::uint8_t> buffer) override
    {
        if (nack_all) {
            return false;
        }
        ++writes;

        if (reg == kReset && buffer.size() == 1U && buffer[0] == 0xB6U) {
            reset();
            return true;
        }
        for (std::size_t i = 0; i < buffer.size(); ++i) {
            regs_[static_cast<std::uint8_t>(reg + i)] = buffer[i];
        }
        if (reg == kCtrlMeas && buffer.size() == 1U && (buffer[0] & 0x03U) == 0x01U) {
            measuring_left_ = 2U;   /* чип зайнятий два опитування поспіль */
        }
        return true;
    }

    /* Те, що робить чип на команду 0xB6. */
    void reset()
    {
        regs_ = nvm_;
        measuring_left_ = 0U;
        im_update_left_ = 2U;
    }

private:
    void load_factory()
    {
        nvm_.fill(0);
        nvm_[kChipId] = 0x60;

        /* Коефіцієнти з прикладу в технічному описі BME280. */
        put_u16(kCalib00 + 0, 27504);
        put_u16(kCalib00 + 2, static_cast<std::uint16_t>(26435));
        put_u16(kCalib00 + 4, static_cast<std::uint16_t>(-1000));
        put_u16(kCalib00 + 6, 36477);
        put_u16(kCalib00 + 8, static_cast<std::uint16_t>(-10685));
        put_u16(kCalib00 + 10, static_cast<std::uint16_t>(3024));
        put_u16(kCalib00 + 12, static_cast<std::uint16_t>(2855));
        put_u16(kCalib00 + 14, static_cast<std::uint16_t>(140));
        put_u16(kCalib00 + 16, static_cast<std::uint16_t>(-7));
        put_u16(kCalib00 + 18, static_cast<std::uint16_t>(15500));
        put_u16(kCalib00 + 20, static_cast<std::uint16_t>(-14600));
        put_u16(kCalib00 + 22, static_cast<std::uint16_t>(6000));

        put_adc(kPressMsb, 415148U);      /* ≈ 1006.5 гПа */
        put_adc(kPressMsb + 3, 519888U);  /* ≈ 25.08 °C */
    }

    void put_adc(std::uint8_t addr, std::uint32_t adc)
    {
        nvm_[addr] = static_cast<std::uint8_t>(adc >> 12);
        nvm_[static_cast<std::uint8_t>(addr + 1)] =
            static_cast<std::uint8_t>((adc >> 4) & 0xFFU);
        nvm_[static_cast<std::uint8_t>(addr + 2)] =
            static_cast<std::uint8_t>((adc << 4) & 0xF0U);
    }

    std::array<std::uint8_t, 256> nvm_{};
    std::array<std::uint8_t, 256> regs_{};
    std::uint8_t measuring_left_{0};
    std::uint8_t im_update_left_{0};
};

int g_checks = 0;

void check(bool cond, const char* what)
{
    ++g_checks;
    if (!cond) {
        std::printf("  ПРОВАЛ: %s\n", what);
        assert(cond);
    }
}

void test_happy_path()
{
    MockChip chip;
    {
        auto adapter = sensor::SensorAdapter::create(chip, 0x76);
        check(adapter.has_value(), "ініціалізація");

        const auto reading = adapter->read();
        check(reading.has_value(), "читання відліку");
        check(reading->temperature_celsius > 24.0F &&
                  reading->temperature_celsius < 26.0F,
              "температура біля 25 °C");
        check(reading->pressure_hpa > 990.0F && reading->pressure_hpa < 1020.0F,
              "тиск біля 1006 гПа");

        chip.writes = 0U;
    }   /* вихід з області видимості — тут спрацьовує деструктор адаптера */
    check(chip.writes > 0U, "RAII переводить чип у сон");
}

void test_bus_nack()
{
    MockChip chip;
    chip.nack_all = true;
    const auto adapter = sensor::SensorAdapter::create(chip, 0x76);
    check(!adapter.has_value(), "об'єкта на мовчазній шині не існує");
    check(adapter.error() == sensor::SensorStatus::CommunicationError,
          "код помилки — CommunicationError");
}

void test_wrong_chip_id()
{
    MockChip chip;
    chip.poke(kChipId, 0x00);   /* помилка монтажу: стоїть не той чип */
    const auto adapter = sensor::SensorAdapter::create(chip, 0x76);
    check(!adapter.has_value() && adapter.error() == sensor::SensorStatus::InvalidDevice,
          "чужий Chip ID дає InvalidDevice");
}

void test_zero_calibration()
{
    MockChip chip;
    chip.put_u16(kCalib00 + 6, 0U);   /* dig_P1 = 0 */
    const auto adapter = sensor::SensorAdapter::create(chip, 0x76);
    check(!adapter.has_value() &&
              adapter.error() == sensor::SensorStatus::CalibrationInvalid,
          "нульове калібрування спинено до ділення на нуль");
}

void test_fault_mid_transaction()
{
    MockChip chip;
    auto adapter = sensor::SensorAdapter::create(chip, 0x76);
    check(adapter.has_value(), "старт");

    chip.fail_reg = kPressMsb;   /* обрив саме на пакеті відліку */
    const auto failed = adapter->read();
    check(!failed.has_value() &&
              failed.error() == sensor::SensorStatus::CommunicationError,
          "збій у транзакції дає CommunicationError");

    /* Блокування зняв scoped_lock на виході — наступне читання проходить. */
    chip.fail_reg.reset();
    check(adapter->read().has_value(), "після збою адаптер працює далі");
}

void test_measure_timeout()
{
    MockChip chip;
    auto adapter = sensor::SensorAdapter::create(chip, 0x76);
    check(adapter.has_value(), "старт");

    chip.stuck_measuring = true;
    const auto stuck = adapter->read();
    check(!stuck.has_value() && stuck.error() == sensor::SensorStatus::Timeout,
          "зависле перетворення дає Timeout, а не вічний цикл");
    chip.stuck_measuring = false;
}

void test_move_keeps_context()
{
    MockChip chip;
    auto created = sensor::SensorAdapter::create(chip, 0x76);
    check(created.has_value(), "старт");

    /* Переміщення не ламає intf_ptr: реалізація лишилась за тією ж адресою. */
    sensor::SensorAdapter moved(std::move(*created));
    check(moved.read().has_value(), "після переміщення давач читається");
}

}  // namespace

int main()
{
    test_happy_path();
    test_bus_nack();
    test_wrong_chip_id();
    test_zero_calibration();
    test_fault_mid_transaction();
    test_measure_timeout();
    test_move_keeps_context();

    std::printf("усі %d перевірок пройдено\n", g_checks);
    return 0;
}
