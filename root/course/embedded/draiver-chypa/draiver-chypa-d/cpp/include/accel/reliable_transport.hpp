// reliable_transport.hpp — повтори, відступ і квантоване очікування.
//
// Надійність не вбудована в драйвер прапорцями, а надіта на транспорт
// декоратором: ReliableTransport сам задовольняє концепт BusTransport, тож
// драйвер про нього не знає нічого. Потрібен голий транспорт для стенда —
// просто не загортайте.
#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <span>
#include <utility>

#include "status.hpp"
#include "transport.hpp"

namespace accel {

template <BusTransport Inner>
class ReliableTransport {
public:
    struct Policy {
        std::uint8_t              retries{3};
        std::chrono::milliseconds backoff{1};
    };

    explicit ReliableTransport(Inner inner, Policy policy = {}) noexcept
        : inner_(std::move(inner)), policy_(policy) {}

    Result<void> read(std::uint8_t reg, std::span<std::uint8_t> rx) noexcept
    {
        return repeat([&] { return inner_.read(reg, rx); });
    }

    Result<void> write(std::uint8_t reg, std::span<const std::uint8_t> tx) noexcept
    {
        return repeat([&] { return inner_.write(reg, tx); });
    }

    void delay(std::chrono::milliseconds pause) noexcept { inner_.delay(pause); }

    [[nodiscard]] Inner &inner() noexcept { return inner_; }

private:
    // Пауза 1, 2, 4, 8 мс: короткий сплеск завади встигає закінчитися, а
    // задача не стоїть довше за свій дедлайн.
    template <typename Operation>
    Result<void> repeat(Operation operation) noexcept
    {
        auto pause = policy_.backoff;
        for (std::uint8_t attempt = 0; attempt <= policy_.retries; ++attempt) {
            if (attempt > 0) {
                inner_.delay(pause);
                pause *= 2;
            }
            if (auto outcome = operation(); outcome.has_value()) {
                return outcome;
            }
        }
        return std::unexpected(Status::CommFail);
    }

    Inner  inner_;
    Policy policy_;
};

// Квантоване очікування прапорця замість while(!flag);. Помилку шини не
// ковтаємо: мовчазна шина — це не «дані ще не готові».
template <BusTransport Transport>
[[nodiscard]] Result<void> waitForFlag(Transport &transport,
                                       std::uint8_t reg,
                                       std::uint8_t mask,
                                       std::chrono::milliseconds timeout,
                                       std::chrono::milliseconds interval = std::chrono::milliseconds{1}) noexcept
{
    if (mask == 0 || interval.count() <= 0) {
        return std::unexpected(Status::InvalidParam);
    }

    for (std::chrono::milliseconds elapsed{0};; elapsed += interval) {
        std::array<std::uint8_t, 1> value{};
        if (auto outcome = transport.read(reg, value); !outcome) {
            return std::unexpected(outcome.error());
        }
        if ((value[0] & mask) != 0) {
            return {};
        }
        if (elapsed >= timeout) {
            return std::unexpected(Status::Timeout);
        }
        transport.delay(interval);
    }
}

} // namespace accel
