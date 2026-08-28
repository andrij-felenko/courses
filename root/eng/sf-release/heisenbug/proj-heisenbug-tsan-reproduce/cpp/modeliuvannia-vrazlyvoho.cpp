#include <iostream>
#include <string_view>
#include <memory>
#include <thread>
#include <vector>

constexpr int NUM_ITERATIONS = 100000;

struct UserStats {
    int user_id{42};
    long long hits{0};
    std::string_view session_tag{"session_init"};
};

static UserStats* g_stats{nullptr};
static bool g_enable_probe_logging{false};

void worker_updater(int thread_id) {
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        if (g_enable_probe_logging) {
            // Спостережницький ефект: вивід у std::cout захоплює внутрішній буфер
            // та синхронізує виконання відносно I/O ядра
            std::cout << "[Thread " << thread_id << "] Iteration " << i << "\n";
        }

        UserStats* s = g_stats;
        if (s != nullptr) {
            // Несинхронізований модифікуючий доступ (Data Race)
            s->hits++;
            if (i % 1000 == 0) {
                s->session_tag = (i % 2000 == 0) ? "session_alpha" : "session_beta";
            }
        }
    }
}

void worker_allocator() {
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        if (g_enable_probe_logging) {
            std::cout << "[Allocator] Resetting buffer at " << i << "\n";
        }

        auto* fresh = new UserStats{42, 0, "session_init"};
        UserStats* old = g_stats;
        g_stats = fresh;

        if (old != nullptr) {
            delete old; // Створює вікно use-after-free для паралельного потоку
        }
    }
}

int main(int argc, char** argv) {
    if (argc > 1 && argv[1][0] == '1') {
        g_enable_probe_logging = true;
        std::cout << "[INFO] Probe logging ENABLED (Observation mode)\n";
    } else {
        std::cout << "[INFO] Running in NATIVE mode (No logging)\n";
    }

    g_stats = new UserStats{42, 0, "root"};

    std::jthread t1(worker_updater, 1);
    std::jthread t2(worker_allocator);

    t1.join();
    t2.join();

    delete g_stats;
    std::cout << "[DONE] Completed test successfully.\n";
    return 0;
}
