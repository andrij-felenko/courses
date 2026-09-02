// Програмна модель кристала, у яку по черзі вносимо описані в статті дефекти
// монтажу. Кожен сценарій має очікуваний вердикт — так модуль валідації
// перевіряє сам себе, не потребуючи плати на столі.
#include "bringup/bus.hpp"
#include "bringup/diagnosis.hpp"
#include "bringup/validator.hpp"

#include <array>
#include <chrono>
#include <cstdlib>
#include <format>
#include <iostream>
#include <optional>
#include <string_view>

namespace {

using namespace std::chrono_literals;
using bringup::Byte;
using bringup::BusError;
using bringup::Fault;
using bringup::Register;

enum class Defect {
    None,
    ChipAbsent,        // чип не пропаяний: ніхто не підтверджує адресу
    SlowPowerOnReset,  // кремній прокидається пізніше, ніж ми починаємо питати
    MisoPullUp,        // CS не падає в нуль: на лінії лише резистор до VDD
    ShortToGround,     // крапля припою між лінією даних і полігоном землі
    I2cBusHang,        // слейв утримує SDA після скидання ведучого
    SpiModeMismatch,   // хибний CPHA: біти зсунуто вліво
    MosiBreak,         // мікротріщина на лінії запису
    ScratchpadBridge   // злиті сусідні тригери конфігураційного регістра
};

class SimulatedChip {
public:
    explicit SimulatedChip(Defect defect) : defect_{defect} {
        if (defect == Defect::SlowPowerOnReset) {
            power_on_reset_ = 40ms;
        }
        registers_[0x75] = 0x68;  // WHO_AM_I: зашитий у кремній паспорт MPU-6050
        registers_[0x19] = 0x07;  // SMPLRT_DIV: робоче значення дільника частоти
    }

    [[nodiscard]] std::expected<Byte, BusError> read(Register reg) noexcept {
        ++reads_;

        switch (defect_) {
            case Defect::ChipAbsent:
                return std::unexpected(BusError::NoAcknowledge);
            case Defect::MisoPullUp:
                return Byte{0xFF};  // вихід чипа у Z-стані, читаємо саму підтяжку
            case Defect::ShortToGround:
            case Defect::I2cBusHang:
                return Byte{0x00};  // лінію тримає припій або завислий слейв
            default:
                break;
        }

        if (clock_ < power_on_reset_) {
            return std::unexpected(BusError::NoAcknowledge);  // ядро ще під скиданням
        }

        Byte value = registers_[reg];
        if (defect_ == Defect::SpiModeMismatch) {
            // Ведучий стробує на пів такту пізніше: старший біт губиться, решта
            // з'їжджає вліво, а знизу підтягується стан спокою лінії.
            value = static_cast<Byte>(value << 1);
        }
        return value;
    }

    [[nodiscard]] std::expected<void, BusError> write(Register reg, Byte value) noexcept {
        ++writes_;

        switch (defect_) {
            case Defect::ChipAbsent:
                return std::unexpected(BusError::NoAcknowledge);
            case Defect::ShortToGround:
            case Defect::I2cBusHang:
                // На притиснутій до землі SDA не видати навіть умови СТАРТ.
                return std::unexpected(BusError::ArbitrationLost);
            default:
                break;
        }

        if (clock_ < power_on_reset_) {
            return std::unexpected(BusError::NoAcknowledge);
        }

        if (defect_ == Defect::MosiBreak) {
            // Периферія ведучого відтактувала кадр і рапортує успіх, але байт
            // до кристала не доїхав: регістр лишається старим.
            return {};
        }

        if (defect_ == Defect::ScratchpadBridge) {
            constexpr Byte kPair = 0x30;  // злиті розряди 4 і 5 комірки конфігурації
            if ((value & kPair) != 0) {
                value = static_cast<Byte>(value | kPair);
            }
        }

        registers_[reg] = value;
        return {};
    }

    void wait(std::chrono::milliseconds pause) noexcept { clock_ += pause; }

    [[nodiscard]] unsigned reads() const noexcept { return reads_; }
    [[nodiscard]] unsigned writes() const noexcept { return writes_; }
    [[nodiscard]] std::chrono::milliseconds clock() const noexcept { return clock_; }

private:
    Defect defect_;
    std::array<Byte, 256> registers_{};
    std::chrono::milliseconds clock_{0};
    std::chrono::milliseconds power_on_reset_{5};
    unsigned reads_{0};
    unsigned writes_{0};
};

static_assert(bringup::BusDriver<SimulatedChip>);

struct Scenario {
    std::string_view title;
    Defect defect;
    std::optional<Fault> expected;  // std::nullopt — чекаємо успіху
};

constexpr std::array<Scenario, 9> kScenarios{{
    {"Справна плата", Defect::None, std::nullopt},
    {"Чип не пропаяний: NACK на адресу", Defect::ChipAbsent, Fault::NoAnswer},
    {"Старт раніше за готовність кремнію (t_POR)", Defect::SlowPowerOnReset, Fault::NoAnswer},
    {"CS не падає: на MISO сама підтяжка", Defect::MisoPullUp, Fault::BusStuckHigh},
    {"Крапля припою: лінія даних на землі", Defect::ShortToGround, Fault::BusStuckLow},
    {"Зависла шина I2C після скидання ведучого", Defect::I2cBusHang, Fault::BusStuckLow},
    {"Хибний режим SPI: CPHA=1 замість 0", Defect::SpiModeMismatch, Fault::BitShift},
    {"Мікротріщина на MOSI: запис не доходить", Defect::MosiBreak, Fault::WritePathDead},
    {"Місток між розрядами конфігураційного регістра", Defect::ScratchpadBridge,
     Fault::ScratchpadCorrupted},
}};

constexpr bringup::DeviceDescriptor kMpu6050{
    .name = "InvenSense MPU-6050",
    .id_reg = 0x75,
    .expected_id = 0x68,
    .scratchpad_reg = 0x19,  // SMPLRT_DIV: вісім живих тригерів без побічних ефектів
    .power_on_delay = 15ms,  // t_POR із запасом для MEMS
    .retry_delay = 2ms,
    .read_attempts = 5,
};

}  // namespace

int main() {
    std::cout << std::format("Первинна валідація {} на модельній платі\n", kMpu6050.name);

    unsigned mismatches = 0;
    unsigned index = 0;

    for (const Scenario& scenario : kScenarios) {
        SimulatedChip chip{scenario.defect};

        std::cout << std::format("\n[{}] {}\n", ++index, scenario.title);

        const auto result = bringup::validate(chip, kMpu6050);
        std::optional<Fault> actual;

        if (result) {
            std::cout << std::format(
                "  статус       : чип живий, обидва напрями шини перевірено\n"
                "  паспорт      : ID 0x{:02X} підтверджено за {} спроб(и), Scratchpad {}\n",
                result->id, result->attempts, result->scratchpad_verified ? "пройдено" : "пропущено");
        } else {
            actual = result.error().fault;
            std::cout << bringup::describe(result.error(), kMpu6050);
        }

        std::cout << std::format("  кадрів шини  : читань {}, записів {}; модельний час {} мс\n",
                                 chip.reads(), chip.writes(), chip.clock().count());

        if (actual != scenario.expected) {
            ++mismatches;
            std::cout << std::format("  !! класифікатор помилився: чекали \"{}\"\n",
                                     scenario.expected ? bringup::title(*scenario.expected)
                                                       : std::string_view{"успіх"});
        }
    }

    std::cout << std::format("\nСценаріїв: {}, розбіжностей класифікації: {}\n", kScenarios.size(),
                             mismatches);
    return mismatches == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
