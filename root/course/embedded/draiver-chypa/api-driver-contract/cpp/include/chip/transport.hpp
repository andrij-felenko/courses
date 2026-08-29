// Контракт платформного шару як концепт: замість структури вказівників на
// функції — вимога до типу, яку компілятор перевіряє на місці підстановки.
// Непрозорого user_ctx тут немає — його роль виконують поля самого
// транспортного обʼєкта, і драйвер їх не бачить за побудовою.
#pragma once

#include <array>
#include <chrono>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "status.hpp"

namespace chip {

/// Рядок кешу Cortex-M7/Cortex-A: під нього вирівнюємо буфери DMA.
inline constexpr std::size_t kCacheLine = 32;

/*
 * Вимоги до транспорту:
 *   read/write  — неподільна транзакція (START · адреса+W · reg ·
 *                 Repeated Start · адреса+R · дані · STOP), із власним
 *                 тайм-аутом і власним захопленням мʼютекса шини;
 *   delay       — квантована затримка, лише з контексту задачі.
 *
 * Якщо транзакцію виконує DMA, інвалідація D-Cache робиться всередині
 * read() перед поверненням: драйвер читає буфер відразу після виходу.
 */
template <typename T>
concept BusTransport = requires(T& bus,
                                std::uint8_t reg,
                                std::span<std::byte> rx,
                                std::span<const std::byte> tx,
                                std::chrono::milliseconds ms) {
    { bus.read(reg, rx) }  -> std::same_as<std::expected<void, Status>>;
    { bus.write(reg, tx) } -> std::same_as<std::expected<void, Status>>;
    { bus.delay(ms) }      -> std::same_as<void>;
};

/*
 * Буфер під пакетне читання. Вирівняний за рядком кешу, розмір кратний
 * йому ж — інвалідація не зачепить сусідніх змінних (false sharing).
 * Розміщує його викликач: тільки він знає, який шматок SRAM доступний
 * контролеру DMA на цій платі (DTCM/CCM здебільшого недоступні).
 */
template <std::size_t N>
struct alignas(kCacheLine) DmaBuffer {
    static_assert(N % kCacheLine == 0, "розмір буфера DMA мусить бути кратним рядку кешу");

    std::array<std::byte, N> storage{};

    [[nodiscard]] std::span<std::byte> head(std::size_t n) noexcept
    {
        return std::span{storage}.first(n);
    }
    [[nodiscard]] std::span<const std::byte> head(std::size_t n) const noexcept
    {
        return std::span{storage}.first(n);
    }
};

} // namespace chip
