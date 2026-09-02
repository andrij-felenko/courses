#pragma once

// Типізована черга ядра. Пам'ять — усередині об'єкта (жодного xQueueCreate
// з купи), приймання повертає std::optional замість pdTRUE та вихідного буфера.
#include "FreeRTOS.h"
#include "queue.h"

#include <array>
#include <cstdint>
#include <optional>
#include <type_traits>

namespace rtos {

template <class T, std::size_t Depth>
class StaticQueue {
    static_assert(std::is_trivially_copyable_v<T>,
                  "черга ядра копіює байти — тип мусить це терпіти");

public:
    StaticQueue() noexcept
        : handle_{xQueueCreateStatic(Depth, sizeof(T), storage_.data(), &control_)}
    {
        configASSERT(handle_ != nullptr);
    }

    StaticQueue(const StaticQueue &) = delete;
    StaticQueue &operator=(const StaticQueue &) = delete;

    bool send(const T &value, TickType_t timeout) noexcept
    {
        return xQueueSend(handle_, &value, timeout) == pdTRUE;
    }

    // Витісняє найстаріше значення, коли споживач відстав: свіжий вимір цінніший.
    void send_newest(const T &value) noexcept
    {
        if (!send(value, 0)) {
            T stale{};
            (void)xQueueReceive(handle_, &stale, 0);
            (void)send(value, 0);
        }
    }

    std::optional<T> receive(TickType_t timeout) noexcept
    {
        T value{};
        if (xQueueReceive(handle_, &value, timeout) == pdTRUE) {
            return value;
        }
        return std::nullopt;
    }

    [[nodiscard]] static constexpr std::size_t bytes() noexcept
    {
        return Depth * sizeof(T) + sizeof(StaticQueue_t);
    }

private:
    std::array<std::uint8_t, Depth * sizeof(T)> storage_{};
    StaticQueue_t control_{};
    QueueHandle_t handle_{nullptr};
};

} // namespace rtos
