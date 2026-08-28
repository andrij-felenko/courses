#include <span>

namespace rtos {

class StreamBufferIsrSender {
public:
    explicit StreamBufferIsrSender(StreamBufferHandle_t handle) noexcept : handle_(handle) {}

    size_t send(std::span<const uint8_t> data, BaseType_t* higher_priority_woken) noexcept {
        return xStreamBufferSendFromISR(handle_, data.data(), data.size(), higher_priority_woken);
    }

private:
    StreamBufferHandle_t handle_;
};

} // namespace rtos
