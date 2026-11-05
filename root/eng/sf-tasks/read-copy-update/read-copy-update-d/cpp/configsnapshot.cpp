#include <atomic>
#include <string>
#include <memory>
#include <iostream>

struct ConfigSnapshot {
    int max_connections;
    std::string server_name;
};

class RcuConfigPublisher {
private:
    std::atomic<ConfigSnapshot*> active_snapshot_{nullptr};

public:
    // Безпечна публікація конфігурації письменником
    void update_config(int max_conn, const std::string& name) {
        // Ініціалізація нового об'єкта в ізольованій пам'яті
        ConfigSnapshot* new_snapshot = new ConfigSnapshot{max_conn, name};

        // store-release встановлює межу: ніякі записи в поля new_snapshot
        // не можуть переставитися ПІСЛЯ атомарної публікації вказівника
        active_snapshot_.store(new_snapshot, std::memory_order_release);
    }

    // Безпечне зчитування конфігурації читачем
    void print_config() const {
        // acquire/consume гарантує, що читання max_connections та server_name
        // виконується ПІСЛЯ завантаження адреси об'єкта
        ConfigSnapshot* snapshot = active_snapshot_.load(std::memory_order_acquire);
        if (snapshot) {
            std::cout << "Server: " << snapshot->server_name 
                      << ", Max Conn: " << snapshot->max_connections << std::endl;
        }
    }
};
