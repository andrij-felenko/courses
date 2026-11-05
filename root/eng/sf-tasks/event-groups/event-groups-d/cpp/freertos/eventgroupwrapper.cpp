#include "FreeRTOS.h"
#include "event_groups.h"
#include <cstdint>

class EventGroupWrapper {
public:
    EventGroupWrapper() : handle_(xEventGroupCreate()) {}

    ~EventGroupWrapper() {
        if (handle_ != nullptr) {
            vEventGroupDelete(handle_);
        }
    }

    // Заборона копіювання об'єкта для збереження ресурсу
    EventGroupWrapper(const EventGroupWrapper&) = delete;
    EventGroupWrapper& operator=(const EventGroupWrapper&) = delete;

    [[nodiscard]] bool is_valid() const noexcept {
        return handle_ != nullptr;
    }

    void set_bits(uint32_t bits) noexcept {
        xEventGroupSetBits(handle_, static_cast<EventBits_t>(bits));
    }

    uint32_t wait_bits(uint32_t bits_to_wait, bool clear_on_exit, bool wait_for_all, TickType_t ticks_to_wait) noexcept {
        return static_cast<uint32_t>(xEventGroupWaitBits(
            handle_,
            static_cast<EventBits_t>(bits_to_wait),
            clear_on_exit ? pdTRUE : pdFALSE,
            wait_for_all ? pdTRUE : pdFALSE,
            ticks_to_wait
        ));
    }

    [[nodiscard]] EventGroupHandle_t native_handle() const noexcept {
        return handle_;
    }

private:
    EventGroupHandle_t handle_{nullptr};
};

namespace SystemEvents {
    constexpr uint32_t BitPowerStable   = (1UL << 0);
    constexpr uint32_t BitSensorReady   = (1UL << 1);
    constexpr uint32_t BitNetworkUp     = (1UL << 2);
    constexpr uint32_t BitSystemReady   = BitPowerStable | BitSensorReady | BitNetworkUp;
}
