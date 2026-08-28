#include <iostream>
#include <memory>
#include <thread>
#include <atomic>
#include <string_view>

struct UserStats {
    int user_id{42};
    std::atomic<long long> hits{0};
    std::string_view session_tag{"session_init"};
};

// Використання std::atomic<std::shared_ptr> для потокобезпечного володіння
static std::shared_ptr<UserStats> g_stats{std::make_shared<UserStats>()};
static std::mutex g_swap_mutex;

void worker_updater_safe(int thread_id) {
    (void)thread_id;
    for (int i = 0; i < 100000; ++i) {
        // Атомарне копіювання розумного вказівника (збільшує лічильник посилань)
        std::shared_ptr<UserStats> local_s = std::atomic_load(&g_stats);
        if (local_s) {
            local_s->hits.fetch_add(1, std::memory_order_relaxed);
        }
    }
}

void worker_allocator_safe() {
    for (int i = 0; i < 100000; ++i) {
        auto fresh = std::make_shared<UserStats>();
        fresh->user_id = 42;

        // Атомарна підміна глобального ресурсу
        std::atomic_store(&g_stats, fresh);
    }
}
