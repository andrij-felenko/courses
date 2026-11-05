#include <cstdint>
#include <cstddef>
#include <atomic>
#include <array>
#include <algorithm>

/* FreeRTOS та CMSIS заголовки */
#include "FreeRTOS.h"
#include "task.h"
#include "core_cm7.h"

/* Шаблонний клас SPSC lock-free кільцевої черги для дескрипторів */
template <typename ItemType, std::size_t Capacity>
class SpscBlockQueue {
    static_assert((Capacity & (Capacity - 1U)) == 0U, "Capacity must be a power of two");

public:
    SpscBlockQueue() : head_{0U}, tail_{0U}, dropped_{0U}, peak_watermark_{0U} {}

    /* Додавання дескриптора з контексту переривання ISR (виробник) */
    bool push_from_isr(const ItemType& item) noexcept {
        const std::uint32_t current_head = head_.load(std::memory_order_relaxed);
        const std::uint32_t current_tail = tail_.load(std::memory_order_acquire);
        const std::uint32_t occupancy = current_head - current_tail;

        if (occupancy >= Capacity) {
            dropped_.fetch_add(1U, std::memory_order_relaxed);
            return false;
        }

        const std::size_t slot = current_head & (Capacity - 1U);
        buffer_[slot] = item;

        /* Оновлення пікової ватерлінії */
        const std::uint32_t next_occ = occupancy + 1U;
        std::uint32_t current_peak = peak_watermark_.load(std::memory_order_relaxed);
        while (next_occ > current_peak && 
               !peak_watermark_.compare_exchange_weak(current_peak, next_occ, std::memory_order_relaxed)) {
        }

        /* Бар'єр пам'яті Release: публікація дескриптора */
        head_.store(current_head + 1U, std::memory_order_release);
        return true;
    }

    /* Вилучення дескриптора у контексті задачі збереження (споживач) */
    bool pop_into_task(ItemType& item) noexcept {
        const std::uint32_t current_tail = tail_.load(std::memory_order_relaxed);
        const std::uint32_t current_head = head_.load(std::memory_order_acquire);

        if (current_tail == current_head) {
            return false;
        }

        const std::size_t slot = current_tail & (Capacity - 1U);
        item = buffer_[slot];

        /* Бар'єр пам'яті Release: звільнення слота */
        tail_.store(current_tail + 1U, std::memory_order_release);
        return true;
    }

    [[nodiscard]] std::uint32_t dropped_count() const noexcept {
        return dropped_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] std::uint32_t peak_watermark() const noexcept {
        return peak_watermark_.load(std::memory_order_relaxed);
    }

private:
    std::array<ItemType, Capacity> buffer_{};
    alignas(32) std::atomic<std::uint32_t> head_;
    alignas(32) std::atomic<std::uint32_t> tail_;
    std::atomic<std::uint32_t> dropped_;
    std::atomic<std::uint32_t> peak_watermark_;
};

/* Дескриптор передачі вибірки */
struct BlockDescriptor {
    std::uint8_t* data{nullptr};
    std::size_t size_bytes{0U};
    std::uint32_t sequence{0U};
    std::uint32_t timestamp{0U};
};

/* Модуль ізоляції затримок накопичувача */
class StorageDecoupler {
public:
    static constexpr std::size_t kQueueCapacity = 16U;
    static constexpr std::size_t kHalfBufferSize = 1024U;
    static constexpr std::size_t kCacheLineSize = 32U;

    StorageDecoupler() = default;

    void initialize(TaskHandle_t storage_task_handle) noexcept {
        storage_task_handle_ = storage_task_handle;
        sequence_counter_ = 0U;
    }

    /* Обробник переривання DMA половинного або повного заповнення */
    void handle_dma_isr(std::uint8_t buffer_index) noexcept {
        BaseType_t higher_priority_task_woken = pdFALSE;

        BlockDescriptor desc{
            .data = ping_pong_storage_[buffer_index].data(),
            .size_bytes = kHalfBufferSize,
            .sequence = sequence_counter_++,
            .timestamp = static_cast<std::uint32_t>(xTaskGetTickCountFromISR())
        };

        if (queue_.push_from_isr(desc) && storage_task_handle_ != nullptr) {
            vTaskNotifyGiveFromISR(storage_task_handle_, &higher_priority_task_woken);
        }

        portYIELD_FROM_ISR(higher_priority_task_woken);
    }

    /* Основний цикл задачі збереження */
    void run_worker_loop() noexcept {
        for (;;) {
            ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

            BlockDescriptor desc;
            while (queue_.pop_into_task(desc)) {
                /* Інвалідація кешу для забезпечення узгодженості */
                SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(desc.data), 
                                             static_cast<int32_t>(desc.size_bytes));

                /* Безпечний запис у накопичувач через апаратний драйвер */
                write_to_storage_media(desc.data, desc.size_bytes);
            }
        }
    }

private:
    static void write_to_storage_media(const std::uint8_t* data, std::size_t size);

    alignas(kCacheLineSize) std::array<std::array<std::uint8_t, kHalfBufferSize>, 2> ping_pong_storage_{};
    SpscBlockQueue<BlockDescriptor, kQueueCapacity> queue_{};
    TaskHandle_t storage_task_handle_{nullptr};
    std::uint32_t sequence_counter_{0U};
};
