#include <iostream>
#include <string>
#include <vector>
#include <deque>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <optional>
#include <expected>
#include <algorithm>
#include <format>

using namespace std::chrono_literals;

/* Декларативні структури даних */
struct DeploymentSpec {
    int desired_replicas{0};
    std::string image;
};

struct DeploymentStatus {
    int current_replicas{0};
    int ready_replicas{0};
};

struct Deployment {
    std::string name;
    DeploymentSpec spec;
    DeploymentStatus status;
    uint64_t resource_version{1};
};

struct Pod {
    std::string name;
    std::string owner_deployment;
    std::string image;
    bool is_ready{true};
};

enum class ReconcileError {
    NotFound,
    VersionConflict,
    CapacityExceeded
};

/* Потокобезпечне сховище стану (etcd emulator) */
class ClusterStore {
public:
    std::optional<Deployment> get_deployment(std::string_view name) {
        std::scoped_lock lock(mutex_);
        if (deployment_ && deployment_->name == name) {
            return *deployment_;
        }
        return std::nullopt;
    }

    std::vector<Pod> get_pods_for_deployment(std::string_view name) {
        std::scoped_lock lock(mutex_);
        std::vector<Pod> result;
        for (const auto& pod : pods_) {
            if (pod.owner_deployment == name) {
                result.push_back(pod);
            }
        }
        return result;
    }

    void create_pod(Pod pod) {
        std::scoped_lock lock(mutex_);
        pods_.push_back(std::move(pod));
    }

    bool delete_pod(std::string_view name) {
        std::scoped_lock lock(mutex_);
        auto it = std::find_if(pods_.begin(), pods_.end(), [&](const Pod& p) {
            return p.name == name;
        });
        if (it != pods_.end()) {
            pods_.erase(it);
            return true;
        }
        return false;
    }

    /* Атомарне оновлення статусу з перевіркою версії (CAS) */
    std::expected<void, ReconcileError> update_deployment_status(
        std::string_view name,
        uint64_t expected_version,
        DeploymentStatus new_status) 
    {
        std::scoped_lock lock(mutex_);
        if (!deployment_ || deployment_->name != name) {
            return std::unexpected(ReconcileError::NotFound);
        }

        if (deployment_->resource_version != expected_version) {
            return std::unexpected(ReconcileError::VersionConflict);
        }

        deployment_->status = new_status;
        global_version_seq_++;
        deployment_->resource_version = global_version_seq_;
        return {};
    }

    void set_deployment(Deployment dep) {
        std::scoped_lock lock(mutex_);
        global_version_seq_++;
        dep.resource_version = global_version_seq_;
        deployment_ = std::move(dep);
    }

    void simulate_pod_crash(size_t count) {
        std::scoped_lock lock(mutex_);
        while (count > 0 && !pods_.empty()) {
            pods_.pop_back();
            count--;
        }
    }

private:
    std::mutex mutex_;
    std::optional<Deployment> deployment_;
    std::vector<Pod> pods_;
    uint64_t global_version_seq_{0};
};

/* Черга завдань з обмеженням частоти повторень (Rate-Limiting Queue) */
class WorkQueue {
public:
    struct Item {
        std::string name;
        int retry_count{0};
        std::chrono::steady_clock::time_point process_after;
    };

    void push(std::string name, int retry_count = 0, std::chrono::milliseconds delay = 0ms) {
        std::scoped_lock lock(mutex_);
        items_.push_back(Item{
            .name = std::move(name),
            .retry_count = retry_count,
            .process_after = std::chrono::steady_clock::now() + delay
        });
        cv_.notify_one();
    }

    std::optional<Item> pop() {
        std::unique_lock lock(mutex_);
        while (items_.empty() && !shutdown_) {
            cv_.wait(lock);
        }

        if (shutdown_ && items_.empty()) {
            return std::nullopt;
        }

        auto now = std::chrono::steady_clock::now();
        for (auto it = items_.begin(); it != items_.end(); ++it) {
            if (it->process_after <= now) {
                Item ready_item = *it;
                items_.erase(it);
                return ready_item;
            }
        }

        /* Якщо готові задачі ще очікують таймер backoff */
        lock.unlock();
        std::this_thread::sleep_for(10ms);
        return pop();
    }

    void stop() {
        std::scoped_lock lock(mutex_);
        shutdown_ = true;
        cv_.notify_all();
    }

private:
    std::mutex mutex_;
    std::condition_variable cv_;
    std::deque<Item> items_;
    bool shutdown_{false};
};

/* Диспетчер узгодження стану */
class DeploymentReconciler {
public:
    DeploymentReconciler(ClusterStore& store, WorkQueue& queue)
        : store_(store), queue_(queue) {}

    std::expected<void, ReconcileError> reconcile(const std::string& name) {
        // 1. Читання знімка бажаного стану
        auto dep_opt = store_.get_deployment(name);
        if (!dep_opt) {
            return std::unexpected(ReconcileError::NotFound);
        }
        const auto& dep = *dep_opt;
        uint64_t expected_version = dep.resource_version;

        // 2. Аналіз активних ресурсів
        auto current_pods = store_.get_pods_for_deployment(name);
        int active_count = static_cast<int>(current_pods.size());

        std::cout << std::format("[Reconciler C++] '{}' | Desired: {} | Active: {} (Ver: {})\n",
                                 name, dep.spec.desired_replicas, active_count, expected_version);

        int delta = dep.spec.desired_replicas - active_count;

        // 3. Коригувальні мутації (Act)
        if (delta > 0) {
            for (int i = 0; i < delta; ++i) {
                Pod p{
                    .name = std::format("{}-{}-{}", name, expected_version, i),
                    .owner_deployment = name,
                    .image = dep.spec.image,
                    .is_ready = true
                };
                std::cout << std::format("  -> Створено Pod: {} [{}]\n", p.name, p.image);
                store_.create_pod(std::move(p));
            }
        } else if (delta < 0) {
            int to_remove = -delta;
            for (const auto& pod : current_pods) {
                if (to_remove <= 0) break;
                std::cout << std::format("  -> Вилучено Pod: {}\n", pod.name);
                store_.delete_pod(pod.name);
                to_remove--;
            }
        }

        // 4. Оновлення статусу через CAS
        DeploymentStatus new_status{
            .current_replicas = dep.spec.desired_replicas,
            .ready_replicas = dep.spec.desired_replicas
        };

        auto update_res = store_.update_deployment_status(name, expected_version, new_status);
        if (!update_res) {
            std::cout << "  [!] Помилка CAS: конкурентна модифікація стану!\n";
            return std::unexpected(update_res.error());
        }

        std::cout << "  [OK] Узгодження успішне.\n";
        return {};
    }

private:
    ClusterStore& store_;
    WorkQueue& queue_;
};

int main() {
    ClusterStore store;
    WorkQueue queue;

    // Створення базового Deployment
    Deployment dep{
        .name = "billing-service",
        .spec = { .desired_replicas = 3, .image = "billing:v1.0" },
        .status = { .current_replicas = 0, .ready_replicas = 0 }
    };
    store.set_deployment(dep);

    DeploymentReconciler reconciler(store, queue);

    // Запуск фонового потоку контролера (C++20 std::jthread)
    std::jthread worker([&](std::stop_token st) {
        while (!st.stop_requested()) {
            auto item = queue.pop();
            if (!item) break;

            auto result = reconciler.reconcile(item->name);
            if (!result) {
                int next_retry = item->retry_count + 1;
                auto delay = 50ms * (1 << std::min(next_retry, 5));
                std::cout << std::format("  [Backoff] Повтор '{}' через {} мс\n", 
                                         item->name, delay.count());
                queue.push(item->name, next_retry, delay);
            }
        }
    });

    std::cout << "\n=== Подія 1: Початкове розгортання 3 подів ===\n";
    queue.push("billing-service");
    std::this_thread::sleep_for(100ms);

    std::cout << "\n=== Подія 2: Симуляція аварії (Crash 2 подів) ===\n";
    store.simulate_pod_crash(2);
    queue.push("billing-service");
    std::this_thread::sleep_for(100ms);

    std::cout << "\n=== Подія 3: Оновлення бажаного стану (5 реплік) ===\n";
    dep.spec.desired_replicas = 5;
    store.set_deployment(dep);
    queue.push("billing-service");
    std::this_thread::sleep_for(100ms);

    queue.stop();
    return 0;
}
