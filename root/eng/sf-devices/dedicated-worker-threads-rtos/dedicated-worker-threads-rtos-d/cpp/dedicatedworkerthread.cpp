#include <zephyr/kernel.h>
#include <cstdint>
#include <cstddef>

// Об'єктно-орієнтований потік-виконавець під Zephyr RTOS
class DedicatedWorkerThread {
public:
    enum class Command : uint8_t {
        ExecuteStorageWrite,
        ProcessTelemetry,
        Shutdown
    };

    struct Message {
        Command cmd;
        uint32_t address;
        void* data_ptr;
        size_t size;
        struct k_sem* done_sem;
    };

    DedicatedWorkerThread(int priority) : priority_(priority) {
        k_msgq_init(&msg_queue_, queue_buffer_, sizeof(Message), QUEUE_CAPACITY);
    }

    bool start() {
        k_tid_t tid = k_thread_create(
            &thread_data_,
            stack_area_,
            K_THREAD_STACK_SIZEOF(stack_area_),
            &DedicatedWorkerThread::thread_entry_point,
            this, nullptr, nullptr,
            priority_, 0, K_NO_WAIT
        );
        return (tid != nullptr);
    }

    bool send_async(Command cmd, uint32_t address, void* data, size_t size) {
        Message msg{cmd, address, data, size, nullptr};
        return (k_msgq_put(&msg_queue_, &msg, K_NO_WAIT) == 0);
    }

    bool send_sync(Command cmd, uint32_t address, void* data, size_t size, k_timeout_t timeout) {
        struct k_sem done_sem;
        k_sem_init(&done_sem, 0, 1);

        Message msg{cmd, address, data, size, &done_sem};
        if (k_msgq_put(&msg_queue_, &msg, timeout) != 0) {
            return false;
        }

        return (k_sem_take(&done_sem, timeout) == 0);
    }

private:
    static constexpr size_t QUEUE_CAPACITY = 8;
    static constexpr size_t STACK_SIZE = 2048;

    K_THREAD_STACK_DEFINE(stack_area_, STACK_SIZE);
    struct k_thread thread_data_;
    struct k_msgq msg_queue_;
    char queue_buffer_[QUEUE_CAPACITY * sizeof(Message)];
    int priority_;

    static void thread_entry_point(void* p1, void* p2, void* p3) {
        auto* self = static_cast<DedicatedWorkerThread*>(p1);
        self->run_event_loop();
    }

    void run_event_loop() {
        Message msg;
        while (true) {
            // Очікування повідомлення у циклі подій
            if (k_msgq_get(&msg_queue_, &msg, K_FOREVER) == 0) {
                dispatch_message(msg);

                if (msg.done_sem != nullptr) {
                    k_sem_give(msg.done_sem);
                }

                if (msg.cmd == Command::Shutdown) {
                    break;
                }
            }
        }
    }

    void dispatch_message(const Message& msg) {
        switch (msg.cmd) {
            case Command::ExecuteStorageWrite:
                // Виконання локальної обробки
                break;
            case Command::ProcessTelemetry:
                // Обробка телеметрії
                break;
            case Command::Shutdown:
                break;
        }
    }
};
