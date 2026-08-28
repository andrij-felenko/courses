#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <array>
#include <format>

constexpr size_t BLOCK_SIZE = 64;

enum class LockMode {
    Null = 0,
    ProtectedRead = 1,
    Exclusive = 2
};

std::string_view to_string(LockMode mode) {
    switch (mode) {
        case LockMode::Null:          return "NL (Unlocked)";
        case LockMode::ProtectedRead: return "PR (Protected Read / Shared)";
        case LockMode::Exclusive:     return "EX (Exclusive)";
    }
    return "Unknown";
}

/* Спільне блокове сховище */
class SharedStorage {
public:
    SharedStorage() {
        std::string initial = "Початкові дані на диску";
        std::copy(initial.begin(), initial.end(), data_.begin());
    }

    void write_block(std::string_view src) {
        std::lock_guard<std::mutex> lock(mutex_);
        data_.fill(0);
        auto len = std::min(src.size(), BLOCK_SIZE - 1);
        std::copy_n(src.data(), len, data_.begin());
    }

    std::string read_block() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return std::string(data_.data());
    }

private:
    mutable std::mutex mutex_;
    std::array<char, BLOCK_SIZE> data_{};
};

class ClusterNode;

/* Розподілений координатор блокувань */
class DlmCoordinator {
public:
    void acquire(ClusterNode& requester, LockMode target, ClusterNode& other);

private:
    std::mutex dlm_mutex_;
    std::condition_variable cv_;
    LockMode granted_mode_{LockMode::Null};
    int owner_node_id_{-1};
    int pr_holders_{0};
};

/* Вузол кластера */
class ClusterNode {
public:
    ClusterNode(int id, std::shared_ptr<SharedStorage> disk, std::shared_ptr<DlmCoordinator> dlm)
        : node_id_(id), disk_(std::move(disk)), dlm_(std::move(dlm)) {}

    int id() const noexcept { return node_id_; }
    LockMode held_mode() const noexcept { return held_mode_; }

    void handle_bast(LockMode requested) {
        std::cout << std::format("[Вузол {}] << Отримано BAST: потрібен режим {} >>\n",
                                 node_id_, to_string(requested));

        if (cache_dirty_) {
            std::cout << std::format("[Вузол {}] BAST: Скидання брудного кешу на диск: \"{}\"\n",
                                     node_id_, local_cache_);
            disk_->write_block(local_cache_);
            cache_dirty_ = false;
        }

        if (requested == LockMode::ProtectedRead && held_mode_ == LockMode::Exclusive) {
            std::cout << std::format("[Вузол {}] BAST: Добровільне пониження блокування EX -> PR\n", node_id_);
            held_mode_ = LockMode::ProtectedRead;
        } else if (requested == LockMode::Exclusive) {
            std::cout << std::format("[Вузол {}] BAST: Інвалідація кешу та звільнення до NL\n", node_id_);
            held_mode_ = LockMode::Null;
            cache_valid_ = false;
        }
    }

    void set_granted(LockMode mode) {
        held_mode_ = mode;
    }

    void write(std::string_view new_data, ClusterNode& other) {
        std::cout << std::format("\n--- [Вузол {}] Початок операції WRITE(\"{}\") ---\n", node_id_, new_data);
        if (held_mode_ != LockMode::Exclusive) {
            dlm_->acquire(*this, LockMode::Exclusive, other);
        }
        local_cache_ = std::string(new_data);
        cache_valid_ = true;
        cache_dirty_ = true;
        std::cout << std::format("[Вузол {}] Запис у локальний Page Cache (cache_dirty = true)\n", node_id_);
    }

    void read(ClusterNode& other) {
        std::cout << std::format("\n--- [Вузол {}] Початок операції READ() ---\n", node_id_);
        if (held_mode_ == LockMode::Null) {
            dlm_->acquire(*this, LockMode::ProtectedRead, other);
        }
        if (!cache_valid_) {
            std::cout << std::format("[Вузол {}] Кеш невалідний! Читання блоку з LUN...\n", node_id_);
            local_cache_ = disk_->read_block();
            cache_valid_ = true;
        } else {
            std::cout << std::format("[Вузол {}] Використання локального кешу сторінок (RAM Hit)\n", node_id_);
        }
        std::cout << std::format("[Вузол {}] Прочитані дані: \"{}\"\n", node_id_, local_cache_);
    }

private:
    int node_id_;
    std::shared_ptr<SharedStorage> disk_;
    std::shared_ptr<DlmCoordinator> dlm_;
    std::string local_cache_;
    bool cache_valid_{false};
    bool cache_dirty_{false};
    LockMode held_mode_{LockMode::Null};
};

void DlmCoordinator::acquire(ClusterNode& requester, LockMode target, ClusterNode& other) {
    std::unique_lock<std::mutex> lock(dlm_mutex_);

    std::cout << std::format("[Вузол {}] Запит блокування {} (поточний: {})\n",
                             requester.id(), to_string(target), to_string(requester.held_mode()));

    if (target == LockMode::ProtectedRead) {
        if (granted_mode_ == LockMode::Exclusive) {
            std::cout << std::format("[DLM] Конфлікт! Виклик BAST на Вузлі {}\n", other.id());
            other.handle_bast(LockMode::ProtectedRead);
            granted_mode_ = LockMode::ProtectedRead;
            owner_node_id_ = -1;
            pr_holders_ = 2; // Обидва вузли мають PR
        } else {
            granted_mode_ = LockMode::ProtectedRead;
            ++pr_holders_;
        }
        requester.set_granted(LockMode::ProtectedRead);
        std::cout << std::format("[Вузол {}] >> CAST: Надано режим PR (читачів: {}) <<\n",
                                 requester.id(), pr_holders_);
    } else if (target == LockMode::Exclusive) {
        if (granted_mode_ != LockMode::Null) {
            std::cout << std::format("[DLM] Конфлікт для EX! Виклик BAST на Вузлі {}\n", other.id());
            other.handle_bast(LockMode::Exclusive);
        }
        granted_mode_ = LockMode::Exclusive;
        owner_node_id_ = requester.id();
        pr_holders_ = 0;
        requester.set_granted(LockMode::Exclusive);
        std::cout << std::format("[Вузол {}] >> CAST: Надано режим EX <<\n", requester.id());
    }
}

int main() {
    auto storage = std::make_shared<SharedStorage>();
    auto dlm = std::make_shared<DlmCoordinator>();

    ClusterNode node_a(1, storage, dlm);
    ClusterNode node_b(2, storage, dlm);

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ SHARED-DISK ТА DLM (C++20) ===\n";

    node_a.write("Оновлення блоку 42 від Вузла 1", node_b);
    node_b.read(node_a);

    std::cout << "\n=== ЗАВЕРШЕННЯ СИМУЛЯЦІЇ ===\n";
    return 0;
}
