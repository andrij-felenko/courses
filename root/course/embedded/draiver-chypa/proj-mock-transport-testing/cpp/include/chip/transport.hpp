// transport.hpp — вимога драйвера до шини, виражена концептом.
//
// Ніякої віртуальної таблиці: драйвер — шаблон, а концепт каже, який саме
// інтерфейс від шини потрібен. На платі підставляють клас поверх периферії
// мікроконтролера, у тестах — мок; обидва компілюються в прямі виклики,
// а помилку в сигнатурі компілятор називає словами, а не сторінкою підстановок.
#pragma once

#include <chrono>
#include <concepts>
#include <cstdint>
#include <expected>
#include <span>

#include "chip/status.hpp"

namespace chip {

// Транспорт представляє ОДИН пристрій на шині: адреса вшита в нього при
// побудові, тому драйверу не треба тягати її крізь кожен виклик.
//
// Контракт: транзакція або відбувається повністю, або не відбувається
// зовсім. Часткове читання — це помилка, а не «скільки встиглося».
template <class T>
concept Transport = requires(T& bus,
                             std::uint8_t reg,
                             std::span<std::uint8_t> in,
                             std::span<const std::uint8_t> out,
                             std::chrono::milliseconds pause) {
    { bus.read(reg, in) } -> std::same_as<std::expected<void, Error>>;
    { bus.write(reg, out) } -> std::same_as<std::expected<void, Error>>;
    { bus.delay(pause) } -> std::same_as<void>;
};

// Політика повторних спроб для короткочасних завад на шині.
struct RetryPolicy {
    unsigned                  maxRetries{3};
    std::chrono::milliseconds baseDelay{1};
};

} // namespace chip
