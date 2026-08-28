#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <stdexcept>
#include <mutex>

class UserLockValidator {
public:
    using LockID = const void*;

    static void on_lock_acquire(LockID lock) {
        auto& current_held = get_held_locks();
        
        for (LockID held : current_held) {
            // Перевіряємо, чи існує зворотне ребро у графі залежностей
            if (has_path(lock, held)) {
                std::cerr << "[LOCKDEP WARNING] Detected potential deadlock cycle! "
                          << "Trying to acquire " << lock 
                          << " while holding " << held << "\n";
                throw std::runtime_error("Deadlock cycle detected by UserLockValidator");
            }
            // Додаємо ребро held -> lock
            get_graph()[held].insert(lock);
        }
        
        current_held.push_back(lock);
    }

    static void on_lock_release(LockID lock) {
        auto& current_held = get_held_locks();
        if (!current_held.empty() && current_held.back() == lock) {
            current_held.pop_back();
        }
    }

private:
    static std::vector<LockID>& get_held_locks() {
        thread_local std::vector<LockID> held;
        return held;
    }

    static std::unordered_map<LockID, std::unordered_set<LockID>>& get_graph() {
        static std::unordered_map<LockID, std::unordered_set<LockID>> graph;
        return graph;
    }

    // Пошук шляху у графі (DFS)
    static bool has_path(LockID start, LockID target) {
        std::unordered_set<LockID> visited;
        std::vector<LockID> stack = {start};

        while (!stack.empty()) {
            LockID curr = stack.back();
            stack.pop_back();

            if (curr == target) return true;

            if (visited.find(curr) == visited.end()) {
                visited.insert(curr);
                auto& neighbors = get_graph()[curr];
                for (LockID next : neighbors) {
                    stack.push_back(next);
                }
            }
        }
        return false;
    }
};

// Обгортка для std::mutex з автоматичною перевіркою
class ValidatedMutex {
public:
    void lock() {
        UserLockValidator::on_lock_acquire(this);
        native_mutex.lock();
    }

    void unlock() {
        native_mutex.unlock();
        UserLockValidator::on_lock_release(this);
    }

private:
    std::mutex native_mutex;
};
