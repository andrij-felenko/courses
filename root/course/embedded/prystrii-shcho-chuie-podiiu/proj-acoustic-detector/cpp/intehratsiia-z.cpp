#include "acoustic_detector.hpp"
#include "FreeRTOS.h"
#include "task.h"

namespace acoustic {

class AudioService {
public:
    static constexpr std::uint32_t EventHalfTransfer = (1 << 0);
    static constexpr std::uint32_t EventFullTransfer = (1 << 1);

    static void init() noexcept {
        instance().detector_.reset();
    }

    static void runTask() noexcept {
        instance().loop();
    }

    static void notifyFromISR(std::uint32_t flag, BaseType_t *higher_woken) noexcept {
        if (instance().task_handle_) {
            xTaskNotifyFromISR(instance().task_handle_, flag, eSetBits, higher_woken);
        }
    }

    static std::array<std::int16_t, FrameSamples * 2>& dmaBuffer() noexcept {
        return instance().dma_buffer_;
    }

private:
    AudioService() = default;

    static AudioService& instance() noexcept {
        static AudioService inst;
        return inst;
    }

    void loop() noexcept {
        task_handle_ = xTaskGetCurrentTaskHandle();
        std::uint32_t flags = 0;

        for (;;) {
            xTaskNotifyWait(0, 0xFFFFFFFF, &flags, portMAX_DELAY);

            if (flags & EventHalfTransfer) {
                detector_.processHalfBuffer(std::span{dma_buffer_.data(), FrameSamples});
            }
            if (flags & EventFullTransfer) {
                detector_.processHalfBuffer(std::span{dma_buffer_.data() + FrameSamples, FrameSamples});
            }

            if (const auto res = detector_.pollEvent(); res.has_value()) {
                if (res->confidence > 0.75f) {
                    handleAcousticAlert(*res);
                }
            }
        }
    }

    void handleAcousticAlert(const DetectionResult &res) noexcept {
        // Формування тривожного пакету телеметрії
        (void)res;
    }

    TaskHandle_t task_handle_{nullptr};
    EventDetector detector_{};
    alignas(4) std::array<std::int16_t, FrameSamples * 2> dma_buffer_{};
};

} // namespace acoustic
