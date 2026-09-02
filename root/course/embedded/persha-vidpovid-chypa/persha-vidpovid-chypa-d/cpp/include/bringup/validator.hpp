// Сама послідовність оживлення: пауза t_POR, читання WHO_AM_I з повторними
// спробами, класифікація аномальних байтів, перевірка бітового зсуву й тест
// Scratchpad з обов'язковим відновленням початкового вмісту регістра.
#pragma once

#include "bringup/bus.hpp"

#include <array>
#include <cassert>
#include <cstddef>

namespace bringup {

// Шаховий патерн ловить містки між сусідніми розрядами, крайні маски —
// залипання вихідних транзисторів у нуль і в одиницю.
inline constexpr std::array<Byte, 4> kScratchpadPatterns{0x55, 0xAA, 0x00, 0xFF};

namespace detail {

// Пара сусідніх розрядів, у які записали різне, а прочитали однакове, —
// це або місток припою, або злиті тригери в кристалі.
[[nodiscard]] constexpr Byte bridged_pairs(Byte written, Byte got) noexcept {
    Byte mask = 0;
    for (unsigned bit = 0; bit + 1 < 8; ++bit) {
        const bool w_lo = (written >> bit) & 1U;
        const bool w_hi = (written >> (bit + 1)) & 1U;
        const bool g_lo = (got >> bit) & 1U;
        const bool g_hi = (got >> (bit + 1)) & 1U;
        if (w_lo != w_hi && g_lo == g_hi) {
            mask = static_cast<Byte>(mask | (0x3U << bit));
        }
    }
    return mask;
}

}  // namespace detail

template <BusDriver Bus>
[[nodiscard]] std::expected<Passport, Failure> validate(Bus& bus, const DeviceDescriptor& device) {
    // Ідентифікатор із самих нулів або самих одиниць неможливо відрізнити від
    // мертвої шини — жоден виробник такого й не призначає.
    assert(device.expected_id != 0x00 && device.expected_id != 0xFF);
    assert(device.read_attempts > 0);

    unsigned attempts = 0;

    // Перехідні процеси живлення тривають довше за один кадр: даємо кристалу
    // ще кілька спроб, замість того щоб здаватися після першого NACK.
    auto read_with_retry = [&](Register reg) -> std::expected<Byte, BusError> {
        std::expected<Byte, BusError> answer = std::unexpected(BusError::Timeout);
        for (unsigned n = 1; n <= device.read_attempts; ++n) {
            attempts = n;
            answer = bus.read(reg);
            if (answer) {
                return answer;
            }
            bus.wait(device.retry_delay);
        }
        return answer;
    };

    // 1. Пауза t_POR: доки детектор скидання тримає ядро, декодер команд
    //    фізично не працює.
    bus.wait(device.power_on_delay);

    // 2. WHO_AM_I.
    const auto id = read_with_retry(device.id_reg);
    if (!id) {
        return std::unexpected(
            Failure{.fault = Fault::NoAnswer, .attempts = attempts, .bus_error = id.error()});
    }

    // 3. Крайні байти — це не дані, а рівні напруги на лінії.
    if (*id == 0xFF) {
        return std::unexpected(
            Failure{.fault = Fault::BusStuckHigh, .received_id = *id, .attempts = attempts});
    }
    if (*id == 0x00) {
        return std::unexpected(
            Failure{.fault = Fault::BusStuckLow, .received_id = *id, .attempts = attempts});
    }

    // 4. Зсув рівно на один розряд: пайка ціла, помилка в конфігурації шини.
    if (*id == static_cast<Byte>(device.expected_id << 1)) {
        return std::unexpected(Failure{.fault = Fault::BitShift,
                                       .received_id = *id,
                                       .shift = Shift::Left,
                                       .attempts = attempts});
    }
    if (*id == static_cast<Byte>(device.expected_id >> 1)) {
        return std::unexpected(Failure{.fault = Fault::BitShift,
                                       .received_id = *id,
                                       .shift = Shift::Right,
                                       .attempts = attempts});
    }

    // 5. Точна звірка з паспортом.
    if (*id != device.expected_id) {
        return std::unexpected(
            Failure{.fault = Fault::ForeignId, .received_id = *id, .attempts = attempts});
    }

    // 6. WHO_AM_I довів лише тракт читання. Тепер повний дуплекс.
    const auto backup = read_with_retry(device.scratchpad_reg);
    if (!backup) {
        return std::unexpected(Failure{.fault = Fault::NoAnswer,
                                       .received_id = *id,
                                       .attempts = attempts,
                                       .bus_error = backup.error()});
    }

    // Конфігураційний регістр лишаємо таким, яким його застали.
    const auto restore = [&] { static_cast<void>(bus.write(device.scratchpad_reg, *backup)); };

    BitDefects defects{};
    bool failed = false;
    Byte first_written = 0;
    Byte first_readback = 0;
    bool every_readback_is_backup = true;
    bool some_pattern_differs = false;

    // Проходимо всі чотири патерни навіть після першої розбіжності: карта
    // несправних бітів корисніша за перший розбіжний байт.
    for (const Byte pattern : kScratchpadPatterns) {
        const auto written = bus.write(device.scratchpad_reg, pattern);
        if (!written) {
            restore();
            return std::unexpected(Failure{.fault = Fault::NoAnswer,
                                           .received_id = *id,
                                           .attempts = attempts,
                                           .bus_error = written.error()});
        }

        const auto readback = bus.read(device.scratchpad_reg);
        if (!readback) {
            restore();
            return std::unexpected(Failure{.fault = Fault::NoAnswer,
                                           .received_id = *id,
                                           .attempts = attempts,
                                           .bus_error = readback.error()});
        }

        if (pattern != *backup) {
            some_pattern_differs = true;
        }
        if (*readback != *backup) {
            every_readback_is_backup = false;
        }

        if (*readback != pattern) {
            defects.stuck_high = static_cast<Byte>(defects.stuck_high | (~pattern & *readback));
            defects.stuck_low = static_cast<Byte>(defects.stuck_low | (pattern & ~*readback));
            defects.bridged =
                static_cast<Byte>(defects.bridged | detail::bridged_pairs(pattern, *readback));
            if (!failed) {
                failed = true;
                first_written = pattern;
                first_readback = *readback;
            }
        }
    }

    restore();

    if (!failed) {
        return Passport{.id = *id, .attempts = attempts, .scratchpad_verified = true};
    }

    // Якщо на кожен патерн повертається старе значення регістра, кристал не
    // бачив жодного нашого байта: обірвано лінію запису, а не окремі біти.
    const bool write_path_dead = every_readback_is_backup && some_pattern_differs;

    return std::unexpected(Failure{
        .fault = write_path_dead ? Fault::WritePathDead : Fault::ScratchpadCorrupted,
        .received_id = *id,
        .written = first_written,
        .readback = first_readback,
        .bits = defects,
        .attempts = attempts,
    });
}

}  // namespace bringup
