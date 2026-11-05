#include <zephyr/kernel.h>
#include <zephyr/sys/cache.h>
#include <cstdint>
#include <cstddef>
#include <span>

// Об'єктно-орієнтований апаратний виконавець під Zephyr RTOS
class DmaWorkerThread {
public:
    enum class EventType : uint8_t {
        DmaBlockReceived,
        StorageFlushRequest,
        Terminate
    };

    struct Event {
        EventType type;
        void* buffer;
        size_t size;
        struct k_sem* completion_sem;
    };

    DmaWorkerThread() {
        k_msgq_init(&msg_queue_, queue_buffer_, sizeof(Event), QUEUE_DEPTH);
        k_mem_slab_init(&buffer_slab_, slab_buffer_, BUFFER_SIZE, BUFFER_COUNT);
    }

    bool start(int priority) {
        k_tid_t tid = k_thread_create(
            &thread_data_,
            stack_area_,
            K_THREAD_STACK_SIZEOF(stack_area_),
            &DmaWorkerThread::thread_entry,
            this, nullptr, nullptr,
            priority, 0, K_NO_WAIT
        );
        return (tid != nullptr);
    }

    void* allocate_dma_buffer() {
        void* ptr = nullptr;
        if (k_mem_slab_alloc(&buffer_slab_, &ptr, K_NO_WAIT) == 0) {
            return ptr;
        }
        return nullptr;
    }

    bool post_event_isr(EventType type, void* buf, size_t len) {
        Event evt{type, buf, len, nullptr};
        return (k_msgq_put(&msg_queue_, &evt, K_NO_WAIT) == 0);
    }

private:
    static constexpr size_t BUFFER_SIZE = 256;
    static constexpr size_t BUFFER_COUNT = 4;
    static constexpr size_t QUEUE_DEPTH = 16;
    static constexpr size_t STACK_SIZE = 2048;

    K_THREAD_STACK_DEFINE(stack_area_, STACK_SIZE);
    struct k_thread thread_data_;
    struct k_msgq msg_queue_;
    struct k_mem_slab buffer_slab_;

    // Вирівнювання пам'яті черги та пулу буферів за лінією кешу
    alignas(32) char queue_buffer_[QUEUE_DEPTH * sizeof(Event)];
    alignas(32) char slab_buffer_[BUFFER_COUNT * BUFFER_SIZE];

    static void thread_entry(void* p1, void*, void*) {
        auto* self = static_cast<DmaWorkerThread*>(p1);
        self->run_loop();
    }

    void run_loop() {
        Event evt;
        while (true) {
            // Очікування події з черги без навантаження на процесор
            if (k_msgq_get(&msg_queue_, &evt, K_FOREVER) == 0) {
                if (evt.type == EventType::Terminate) {
                    if (evt.completion_sem != nullptr) {
                        k_sem_give(evt.completion_sem);
                    }
                    break;
                }

                handle_event(evt);

                if (evt.completion_sem != nullptr) {
                    k_sem_give(evt.completion_sem);
                }

                if (evt.buffer != nullptr) {
                    k_mem_slab_free(&buffer_slab_, evt.buffer);
                }
            }
        }
    }

    void handle_event(const Event& evt) {
        if (evt.buffer == nullptr || evt.size == 0) {
            return;
        }

        // Апаратна інвалідація кеш-пам'яті перед доступом до буфера
        sys_cache_data_invd_range(evt.buffer, evt.size);

        // Безпечний розбір кадру через std::span
        std::span<const uint8_t> payload(static_cast<const uint8_t*>(evt.buffer), evt.size);
        
        volatile uint32_t accumulator = 0;
        for (uint8_t byte : payload) {
            accumulator += byte;
        }
        (void)accumulator;
    }
};
