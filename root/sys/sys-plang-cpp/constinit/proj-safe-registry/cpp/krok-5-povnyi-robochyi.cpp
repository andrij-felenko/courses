#include <iostream>
#include <string_view>
#include <atomic>
#include <thread>
#include <vector>

// ── Оголошення структур реєстру ─────────────────────────────────────────────
struct SubsystemNode {
    std::string_view name;
    uint32_t priority;
    void (*initialize_fn)();
    SubsystemNode* next{nullptr};

    constexpr SubsystemNode(std::string_view n, uint32_t p, void (*init)()) noexcept
        : name(n), priority(p), initialize_fn(init), next(nullptr) {}
};

class SubsystemRegistry {
private:
    std::atomic<SubsystemNode*> head_{nullptr};
    std::atomic<size_t> count_{0};

public:
    constexpr SubsystemRegistry() noexcept : head_(nullptr), count_(0) {}

    void register_subsystem(SubsystemNode* node) noexcept {
        if (!node) return;
        SubsystemNode* current_head = head_.load(std::memory_order_relaxed);
        do {
            node->next = current_head;
        } while (!head_.compare_exchange_weak(
            current_head, node,
            std::memory_order_release,
            std::memory_order_relaxed
        ));
        count_.fetch_add(1, std::memory_order_relaxed);
    }

    void start_all() const {
        SubsystemNode* curr = head_.load(std::memory_order_acquire);
        while (curr) {
            std::cout << "[Реєстр] Ініціалізація підсистеми: " << curr->name 
                      << " (пріоритет: " << curr->priority << ")\n";
            if (curr->initialize_fn) {
                curr->initialize_fn();
            }
            curr = curr->next;
        }
    }

    [[nodiscard]] size_t size() const noexcept {
        return count_.load(std::memory_order_relaxed);
    }
};

// Єдиний екземпляр реєстру, доступний для всіх модулів
inline constinit SubsystemRegistry g_registry{};

class AutoRegister {
public:
    AutoRegister(SubsystemNode& node) noexcept {
        g_registry.register_subsystem(&node);
    }
};

// ── Модуль 1: Драйвер пам'яті (імітація memory_subsystem.cpp) ────────────────
void init_memory() {
    std::cout << "  -> [Memory] Менеджер віртуальної пам'яті активовано.\n";
}
static SubsystemNode s_mem_node{"VirtualMemoryManager", 100, init_memory};
static AutoRegister s_mem_reg{s_mem_node};

// ── Модуль 2: Мережевий стек (імітація network_subsystem.cpp) ────────────────
void init_network() {
    std::cout << "  -> [Network] Мережевий стек готовий приймати пакети.\n";
}
static SubsystemNode s_net_node{"NetworkStack", 200, init_network};
static AutoRegister s_net_reg{s_net_node};

// ── Модуль 3: Аудіо підсистема (імітація audio_subsystem.cpp) ────────────────
void init_audio() {
    std::cout << "  -> [Audio] Аудіо підсистему синхронізовано з апаратним кодеком.\n";
}
static SubsystemNode s_audio_node{"AudioEngine", 50, init_audio};
static AutoRegister s_audio_reg{s_audio_node};

// ── Потоковий трекер подій ──────────────────────────────────────────────────
struct WorkerStats {
    uint64_t tasks_processed{0};
    constexpr WorkerStats() noexcept = default;
};

constinit thread_local WorkerStats t_stats{};

void worker_thread_task(int thread_id) {
    for (int i = 0; i < 10000; ++i) {
        t_stats.tasks_processed++;
    }
    std::cout << "[Потік " << thread_id << "] Оброблено задач: " 
              << t_stats.tasks_processed << "\n";
}

// ── Точка входу в програму ─────────────────────────────────────────────────
int main() {
    std::cout << "=== Запуск програми ===\n";
    std::cout << "Кількість модулів, зареєстрованих до входу в main(): " 
              << g_registry.size() << "\n\n";

    // Старт усіх зареєстрованих компонентів
    g_registry.start_all();
    std::cout << "\n";

    // Створення пулу потоків
    std::vector<std::jthread> workers;
    for (int i = 1; i <= 3; ++i) {
        workers.emplace_back(worker_thread_task, i);
    }

    for (auto& w : workers) {
        if (w.joinable()) {
            w.join();
        }
    }

    std::cout << "\n=== Програму успішно завершено без SIOF та витоків пам'яті ===\n";
    return 0;
}
