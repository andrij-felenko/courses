// Код помилки інженерові на столі не допомагає — потрібен перший крок
// перевірки. Тут розшифрування звіту й таблиця відомих заводських
// ідентифікаторів.
#pragma once

#include "bringup/bus.hpp"

#include <algorithm>
#include <array>
#include <format>
#include <optional>
#include <string>
#include <string_view>

namespace bringup {

struct KnownChip {
    std::string_view name;
    Register id_reg;
    Byte id;
};

inline constexpr std::array<KnownChip, 8> kKnownChips{{
    {"InvenSense MPU-6050", 0x75, 0x68},
    {"InvenSense MPU-9250", 0x75, 0x71},
    {"InvenSense MPU-9255", 0x75, 0x73},
    {"Bosch BME280", 0xD0, 0x60},
    {"Bosch BMP280", 0xD0, 0x58},
    {"ST LIS3DH", 0x0F, 0x33},
    {"ST LSM6DS3", 0x0F, 0x69},
    {"Analog Devices ADXL345", 0x00, 0xE5},
}};

[[nodiscard]] constexpr std::optional<std::string_view> identify(Register id_reg, Byte id) noexcept {
    const auto it = std::ranges::find_if(kKnownChips, [&](const KnownChip& chip) {
        return chip.id_reg == id_reg && chip.id == id;
    });
    if (it == kKnownChips.end()) {
        return std::nullopt;
    }
    return it->name;
}

[[nodiscard]] constexpr std::string_view title(Fault fault) noexcept {
    switch (fault) {
        case Fault::NoAnswer:
            return "відповіді немає: NACK або тайм-аут на фізичному рівні";
        case Fault::BusStuckHigh:
            return "0xFF: лінія весь кадр трималася на рівні підтяжки";
        case Fault::BusStuckLow:
            return "0x00: лінія весь кадр трималася на землі";
        case Fault::BitShift:
            return "ID зсунуто на один розряд: пайка ціла, збита фаза шини";
        case Fault::ForeignId:
            return "відповів не той кремній, якого ми чекали";
        case Fault::WritePathDead:
            return "читання працює, запис до кристала не доходить";
        case Fault::ScratchpadCorrupted:
            return "запис доходить, але біти спотворюються";
    }
    return "невідомий стан";
}

[[nodiscard]] constexpr std::string_view first_step(Fault fault) noexcept {
    switch (fault) {
        case Fault::NoAnswer:
            return "виміряти VDD просто на блокувальному конденсаторі чипа; перевірити вивід "
                   "RESET/NRST і чи витримано паузу t_POR після подачі живлення";
        case Fault::BusStuckHigh:
            return "логічним аналізатором подивитися CS і SCK: чи падає CS у нуль і чи є такти; "
                   "на I2C — чи не зсунуто 7-бітну адресу на біт R/W";
        case Fault::BusStuckLow:
            return "знеструмити плату й виміряти опір SDA/MISO до GND; якщо більше за 10 кОм — "
                   "видати 9 тактів SCL, щоб розчепити завислий автомат слейва";
        case Fault::BitShift:
            return "звірити CPOL/CPHA з даташитом і знизити частоту SCK удвічі; на I2C — "
                   "перевірити, чи не подано 8-бітну адресу замість 7-бітної";
        case Fault::ForeignId:
            return "прочитати маркування SMD на корпусі та перевірити адресний вивід AD0/SDO — "
                   "можливо, відповідає сусідній чип на тій самій адресі";
        case Fault::WritePathDead:
            return "продзвонити MOSI (або SDA) від ніжки мікроконтролера до ніжки чипа; "
                   "перевірити, чи обраний регістр не Read-Only і чи чип не в режимі Sleep";
        case Fault::ScratchpadCorrupted:
            return "оглянути сусідні ніжки під мікроскопом на містки припою; перевірити довжину "
                   "шлейфа й узгодження ліній, знизити частоту шини";
    }
    return "перечитати звіт";
}

[[nodiscard]] constexpr std::string_view bus_error_text(std::optional<BusError> error) noexcept {
    if (!error) {
        return "без деталей";
    }
    switch (*error) {
        case BusError::NoAcknowledge:
            return "NACK на адресу";
        case BusError::Timeout:
            return "тайм-аут кадру";
        case BusError::ArbitrationLost:
            return "втрачений арбітраж";
    }
    return "невідома помилка шини";
}

[[nodiscard]] inline std::string bits_of(Byte value) {
    std::string text(8, '0');
    for (std::size_t i = 0; i < 8; ++i) {
        if (value & (1U << (7 - i))) {
            text[i] = '1';
        }
    }
    return text;
}

[[nodiscard]] inline std::string describe(const Failure& failure, const DeviceDescriptor& device) {
    std::string report = std::format("  статус       : {}\n", title(failure.fault));

    if (failure.fault == Fault::NoAnswer) {
        report += std::format("  WHO_AM_I[0x{:02X}]: жодна з {} спроб не дочекалася підтвердження ({})\n",
                              device.id_reg, failure.attempts, bus_error_text(failure.bus_error));
    } else {
        report += std::format("  WHO_AM_I[0x{:02X}]: очікували 0x{:02X}, прочитали 0x{:02X} (0b{}), спроб {}\n",
                              device.id_reg, device.expected_id, failure.received_id,
                              bits_of(failure.received_id), failure.attempts);
    }

    switch (failure.fault) {
        case Fault::BitShift:
            report += std::format("  зсув         : {} (0x{:02X} {} 1 = 0x{:02X}) — кремній оригінальний\n",
                                  failure.shift == Shift::Left
                                      ? "вліво, ведучий запізнюється на пів такту"
                                      : "вправо, ведучий стробує зарано",
                                  device.expected_id, failure.shift == Shift::Left ? "<<" : ">>",
                                  failure.received_id);
            break;
        case Fault::ForeignId:
            if (const auto neighbour = identify(device.id_reg, failure.received_id)) {
                report += std::format("  за таблицею  : 0x{:02X} — це {}, на платі не той компонент\n",
                                      failure.received_id, *neighbour);
            } else {
                report += std::format("  за таблицею  : 0x{:02X} не належить жодному відомому чипу\n",
                                      failure.received_id);
            }
            break;
        case Fault::WritePathDead:
            report += std::format("  Scratchpad[0x{:02X}]: писали 0x{:02X}, читається старе 0x{:02X} — "
                                  "байт до кристала не дійшов\n",
                                  device.scratchpad_reg, failure.written, failure.readback);
            break;
        case Fault::ScratchpadCorrupted:
            report += std::format("  Scratchpad[0x{:02X}]: 0b{} → 0b{}\n", device.scratchpad_reg,
                                  bits_of(failure.written), bits_of(failure.readback));
            if (failure.bits.bridged != 0) {
                report += std::format("  містки       : 0b{} (сусідні розряди злиті між собою)\n",
                                      bits_of(failure.bits.bridged));
            }
            if (failure.bits.stuck_high != 0) {
                report += std::format("  залипання в 1: 0b{}\n", bits_of(failure.bits.stuck_high));
            }
            if (failure.bits.stuck_low != 0) {
                report += std::format("  залипання в 0: 0b{}\n", bits_of(failure.bits.stuck_low));
            }
            break;
        default:
            break;
    }

    report += std::format("  перший крок  : {}\n", first_step(failure.fault));
    return report;
}

}  // namespace bringup
