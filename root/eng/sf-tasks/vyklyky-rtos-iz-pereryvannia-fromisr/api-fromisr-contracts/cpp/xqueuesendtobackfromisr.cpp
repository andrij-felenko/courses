#include <concepts>
#include <expected>

namespace rtos {

template <typename T>
class QueueIsrEndpoint {
public:
    explicit QueueIsrEndpoint(QueueHandle_t handle) noexcept : handle_(handle) {}

    [[nodiscard]] std::expected<void, BaseType_t> send(
        const T& item,
        BaseType_t* higher_priority_woken
    ) noexcept {
        BaseType_t status = xQueueSendFromISR(handle_, &item, higher_priority_woken);
        if (status == pdPASS) {
            return {};
        }
        return std::unexpected(status);
    }

private:
    QueueHandle_t handle_;
};

} // namespace rtos
