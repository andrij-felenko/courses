#include <atomic>
#include <vector>
#include <iostream>

// Вузол неблокувальної структури даних
struct Node {
    int data;
    Node* next{nullptr};
    explicit Node(int val) : data(val) {}
};

// Запис про вилучений вузол у черзі відстроченого знищення
struct DeferredNode {
    Node* ptr;
    uint64_t epoch_retired;
};

class EpochManager {
public:
    static constexpr size_t NUM_EPOCHS = 3;
    std::atomic<uint64_t> global_epoch{0};

    struct ThreadState {
        std::atomic<bool> active{false};
        std::atomic<uint64_t> local_epoch{0};
    };

    // Оголошення входу потоку в критичну секцію читання
    void enter_critical(ThreadState& tstate) {
        tstate.active.store(true, std::memory_order_relaxed);
        uint64_t current = global_epoch.load(std::memory_order_acquire);
        tstate.local_epoch.store(current, std::memory_order_relaxed);
    }

    // Вихід з критичної секції
    void leave_critical(ThreadState& tstate) {
        tstate.active.store(false, std::memory_order_release);
    }

    // Реєстрація вузла у списку відстроченого видалення
    void retire_node(Node* node, std::vector<DeferredNode>& thread_limbo) {
        uint64_t current = global_epoch.load(std::memory_order_relaxed);
        thread_limbo.push_back({node, current});
    }

    // Спроба просування епохи та очищення старого списку limbo list
    void try_reclaim(const std::vector<ThreadState*>& all_threads, std::vector<DeferredNode>& thread_limbo) {
        uint64_t current = global_epoch.load(std::memory_order_relaxed);

        // Перевірка: чи всі активні потоки знаходяться в поточній епосі
        for (auto* tstate : all_threads) {
            if (tstate->active.load(std::memory_order_acquire)) {
                if (tstate->local_epoch.load(std::memory_order_relaxed) != current) {
                    return; // Є потік, який ще обробляє попередню епоху
                }
            }
        }

        // Просуваємо глобальну епоху
        global_epoch.fetch_add(1, std::memory_order_acq_rel);

        // Безпечно видаляємо вузли, зняті 2 або більше епох тому
        auto it = thread_limbo.begin();
        while (it != thread_limbo.end()) {
            if (current >= it->epoch_retired + 2) {
                delete it->ptr;
                it = thread_limbo.erase(it);
            } else {
                ++it;
            }
        }
    }
};
