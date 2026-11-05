#include "ff.h"
#include "FreeRTOS.h"
#include "task.h"
#include <cstdint>
#include <array>
#include <atomic>
#include <cstring>

template <std::size_t BufferSize = 32 * 1024>
class DmaDoubleBufferLogger {
public:
    static constexpr std::size_t kCacheAlignment = 32;

    explicit DmaDoubleBufferLogger(FIL& target_file)
        : file_(target_file), active_buf_(buf_a_.data()), flush_buf_(buf_b_.data()) {}

    void setConsumerTask(TaskHandle_t task) noexcept {
        consumer_task_ = task;
    }

    bool append(const void* data, std::size_t length) noexcept {
        if (bytes_written_ + length > BufferSize) {
            if (is_flushing_.load(std::memory_order_acquire)) {
                return false; // Буфер переповнено через затримку SD-карти
            }

            // Рокіровка активного та фонового буферів
            std::swap(active_buf_, flush_buf_);
            bytes_written_ = 0;
            is_flushing_.store(true, std::memory_order_release);

            if (consumer_task_ != nullptr) {
                xTaskNotifyGive(consumer_task_);
            }
        }

        std::memcpy(active_buf_ + bytes_written_, data, length);
        bytes_written_ += length;
        return true;
    }

    void processFlush() noexcept {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        UINT written = 0;
        // Запис кластера у попередньо виділену область FatFs
        f_write(&file_, flush_buf_, BufferSize, &written);

        is_flushing_.store(false, std::memory_order_release);
    }

private:
    FIL& file_;
    TaskHandle_t consumer_task_{nullptr};

    alignas(kCacheAlignment) std::array<uint8_t, BufferSize> buf_a_{};
    alignas(kCacheAlignment) std::array<uint8_t, BufferSize> buf_b_{};

    uint8_t* active_buf_{nullptr};
    uint8_t* flush_buf_{nullptr};
    std::size_t bytes_written_{0};
    std::atomic<bool> is_flushing_{false};
};
