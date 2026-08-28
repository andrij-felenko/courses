#include <iostream>
#include <vector>
#include <array>
#include <thread>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <system_error>
#include <cerrno>
#include <span>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>

class Futex2 {
public:
    static int waitv(std::span<futex_waitv> waiters, 
                     const struct timespec* timeout = nullptr, 
                     clockid_t clockid = CLOCK_MONOTONIC) {
        int res = static_cast<int>(::syscall(SYS_futex_waitv, waiters.data(), 
                                             static_cast<unsigned int>(waiters.size()), 
                                             0, timeout, clockid));
        if (res < 0) {
            throw std::system_error(errno, std::generic_category(), "futex_waitv failed");
        }
        return res;
    }

    static void wake(std::atomic<uint32_t>& futex_var, int count = 1) {
        ::syscall(SYS_futex, reinterpret_cast<uint32_t*>(&futex_var), 
                  FUTEX_WAKE | FUTEX_PRIVATE_FLAG, count, nullptr, nullptr, 0);
    }
};

int main() {
    std::atomic<uint32_t> task_done{0};
    std::atomic<uint32_t> shutdown{0};

    std::thread worker([&task_done]() {
        std::cout << "[Worker] Обчислення у C++...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        
        task_done.store(1, std::memory_order_release);
        Futex2::wake(task_done, 1);
    });

    std::array<futex_waitv, 2> waiters{{
        {
            .val = 0,
            .uaddr = reinterpret_cast<uint64_t>(&task_done),
            .flags = FUTEX_32 | FUTEX_PRIVATE_FLAG,
            .__reserved = 0
        },
        {
            .val = 0,
            .uaddr = reinterpret_cast<uint64_t>(&shutdown),
            .flags = FUTEX_32 | FUTEX_PRIVATE_FLAG,
            .__reserved = 0
        }
    }};

    try {
        std::cout << "[Main] Чекаємо через Futex2::waitv...\n";
        int index = Futex2::waitv(waiters);
        std::cout << "[Main] Успішно розбуджено об'єкт з індексом: " << index << "\n";
    } catch (const std::system_error& e) {
        std::cerr << "[Main] Помилка очікування: " << e.what() << "\n";
    }

    worker.join();
    return 0;
}
