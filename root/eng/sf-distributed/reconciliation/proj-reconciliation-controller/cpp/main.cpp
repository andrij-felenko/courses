#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <random>
#include <algorithm>
#include <memory>
#include <optional>

// --- Моделі даних ---
struct NodeSpec {
    int target_replicas{0};
    std::string instance_type{"standard-2cpu-4gb"};
};

struct NodeStatus {
    int available_replicas{0};
    std::string phase{"Pending"};
    std::vector<std::string> active_instance_ids;
};

struct ManagedCluster {
    std::string key;
    uint64_t resource_version{1};
    bool deletion_timestamp{false};
    std::vector<std::string> finalizers;
    NodeSpec spec;
    NodeStatus status;
};

// --- Результат звірки ---
struct ReconcileResult {
    bool requeue{false};
    std::chrono::milliseconds requeue_after{0};
};

// --- Потокобезпечна черга завдань із коалесценцією та бекофом ---
class RateLimitingWorkQueue {
public:
    void add(const std::string& key) {
        std::unique_lock<std::mutex> lock(mtx_);
        dirty_set_.insert(key);
        if (processing_set_.find(key) == processing_set_.end()) {
            if (queued_set_.find(key) == queued_set_.end()) {
                queue_.push(key);
                queued_set_.insert(key);
                cv_.notify_one();
            }
        }
    }

    std::optional<std::string> get() {
        std::unique_lock<std::mutex> lock(mtx_);
        while (queue_.empty() && !shutdown_) {
            cv_.wait(lock);
        }
        if (shutdown_ && queue_.empty()) return std::nullopt;

        std::string key = queue_.front();
        queue_.pop();
        queued_set_.erase(key);
        dirty_set_.erase(key);
        processing_set_.insert(key);
        return key;
    }

    void done(const std::string& key, bool success) {
        std::unique_lock<std::mutex> lock(mtx_);
        processing_set_.erase(key);

        if (!success) {
            int attempts = ++failure_counts_[key];
            // Експоненційний бекоф: base * 2^(attempts-1) + jitter
            int delay_ms = std::min(5000, 100 * (1 << std::min(attempts, 6)));
            std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms / 2));
            dirty_set_.insert(key);
        } else {
            failure_counts_.erase(key);
        }

        // Якщо за час обробки надійшли нові події, повертаємо ключ у чергу
        if (dirty_set_.find(key) != dirty_set_.end() && queued_set_.find(key) == queued_set_.end()) {
            queue_.push(key);
            queued_set_.insert(key);
            cv_.notify_one();
        }
    }

    void shutdown() {
        std::unique_lock<std::mutex> lock(mtx_);
        shutdown_ = true;
        cv_.notify_all();
    }

private:
    std::mutex mtx_;
    std::condition_variable cv_;
    std::queue<std::string> queue_;
    std::unordered_set<std::string> queued_set_;
    std::unordered_set<std::string> dirty_set_;
    std::unordered_set<std::string> processing_set_;
    std::unordered_map<std::string, int> failure_counts_;
    bool shutdown_{false};
};

// --- Імітатор хмарного провайдера (Cloud IaaS API) ---
class CloudProviderDriver {
public:
    std::vector<std::string> list_instances(const std::string& cluster_key) {
        std::lock_guard<std::mutex> lock(mtx_);
        return cloud_vms_[cluster_key];
    }

    std::string create_instance(const std::string& cluster_key, const std::string& type) {
        std::lock_guard<std::mutex> lock(mtx_);
        static uint64_t id_counter = 100;
        std::string vm_id = "vm-" + std::to_string(++id_counter);
        cloud_vms_[cluster_key].push_back(vm_id);
        std::cout << "  [Cloud API] Створено фізичну VM: " << vm_id 
                  << " (тип: " << type << ") для " << cluster_key << std::endl;
        return vm_id;
    }

    void delete_instance(const std::string& cluster_key, const std::string& vm_id) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto& vms = cloud_vms_[cluster_key];
        vms.erase(std::remove(vms.begin(), vms.end(), vm_id), vms.end());
        std::cout << "  [Cloud API] Видалено фізичну VM: " << vm_id 
                  << " з " << cluster_key << std::endl;
    }

private:
    std::mutex mtx_;
    std::unordered_map<std::string, std::vector<std::string>> cloud_vms_;
};

// --- Сховище стану (etcd-подібний транзакційний шар) ---
class ClusterStore {
public:
    std::optional<ManagedCluster> get(const std::string& key) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = store_.find(key);
        if (it == store_.end()) return std::nullopt;
        return it->second;
    }

    // Оптимістичне блокування (Compare-And-Swap)
    bool update(const ManagedCluster& cluster) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = store_.find(cluster.key);
        if (it == store_.end()) return false;
        if (it->second.resource_version != cluster.resource_version) {
            std::cout << "  [Store CAS] Конфлікт версій для " << cluster.key 
                      << " (очікувалась " << cluster.resource_version 
                      << ", знайдено " << it->second.resource_version << ")" << std::endl;
            return false;
        }
        ManagedCluster updated = cluster;
        updated.resource_version++;
        store_[cluster.key] = updated;
        return true;
    }

    void save_initial(const ManagedCluster& cluster) {
        std::lock_guard<std::mutex> lock(mtx_);
        store_[cluster.key] = cluster;
    }

    void remove(const std::string& key) {
        std::lock_guard<std::mutex> lock(mtx_);
        store_.erase(key);
    }

private:
    std::mutex mtx_;
    std::unordered_map<std::string, ManagedCluster> store_;
};

// --- Контролер узгодження ---
class ClusterReconciler {
public:
    ClusterReconciler(std::shared_ptr<ClusterStore> store,
                      std::shared_ptr<CloudProviderDriver> cloud,
                      std::shared_ptr<RateLimitingWorkQueue> queue)
        : store_(store), cloud_(cloud), queue_(queue) {}

    ReconcileResult reconcile(const std::string& key) {
        std::cout << "\n>>> [Reconcile] Початок звірки для ресурсу: " << key << std::endl;

        // 1. Спостереження (Observe)
        auto cluster_opt = store_->get(key);
        if (!cluster_opt.has_value()) {
            std::cout << "  [Observe] Об'єкт " << key << " видалено зі сховища. Завершення." << std::endl;
            return ReconcileResult{false};
        }
        ManagedCluster cluster = cluster_opt.value();

        const std::string finalizer_name = "infra.example.com/cleanup-vms";

        // Обробка безпечного видалення через фіналізатор
        if (cluster.deletion_timestamp) {
            std::cout << "  [Observe] Виявлено мітку видалення (DeletionTimestamp)." << std::endl;
            if (std::find(cluster.finalizers.begin(), cluster.finalizers.end(), finalizer_name) != cluster.finalizers.end()) {
                std::cout << "  [Act: Cleanup] Зупинка фізичних VM перед видаленням метаданих..." << std::endl;
                auto physical_vms = cloud_->list_instances(key);
                for (const auto& vm_id : physical_vms) {
                    cloud_->delete_instance(key, vm_id);
                }
                // Видаляємо фіналізатор
                cluster.finalizers.erase(
                    std::remove(cluster.finalizers.begin(), cluster.finalizers.end(), finalizer_name),
                    cluster.finalizers.end()
                );
                if (!store_->update(cluster)) {
                    return ReconcileResult{true, std::chrono::milliseconds(100)}; // Requeue на конфлікті
                }
                std::cout << "  [Cleanup] Фіналізатор видалено. Ресурс очищено повністю." << std::endl;
            }
            return ReconcileResult{false};
        }

        // Переконуємося, що фіналізатор присутній
        if (std::find(cluster.finalizers.begin(), cluster.finalizers.end(), finalizer_name) == cluster.finalizers.end()) {
            cluster.finalizers.push_back(finalizer_name);
            if (!store_->update(cluster)) {
                return ReconcileResult{true, std::chrono::milliseconds(100)};
            }
            return ReconcileResult{false};
        }

        // Читаємо стан фізичного світу
        std::vector<std::string> current_vms = cloud_->list_instances(key);

        // 2. Аналіз розбіжностей (Diff)
        int desired_count = cluster.spec.target_replicas;
        int actual_count = static_cast<int>(current_vms.size());
        int delta = desired_count - actual_count;

        std::cout << "  [Diff] Бажано: " << desired_count 
                  << " VM, Фактично працює: " << actual_count 
                  << " VM -> Дельта Δ = " << delta << std::endl;

        // 3. Дія (Act & Converge)
        if (delta > 0) {
            std::cout << "  [Act] Створення " << delta << " відсутніх VM..." << std::endl;
            for (int i = 0; i < delta; ++i) {
                cloud_->create_instance(key, cluster.spec.instance_type);
            }
        } else if (delta < 0) {
            int to_remove = -delta;
            std::cout << "  [Act] Видалення " << to_remove << " надлишкових VM..." << std::endl;
            for (int i = 0; i < to_remove; ++i) {
                cloud_->delete_instance(key, current_vms[i]);
            }
        }

        // Оновлюємо спостережуваний статус (Status)
        auto updated_vms = cloud_->list_instances(key);
        cluster.status.available_replicas = static_cast<int>(updated_vms.size());
        cluster.status.active_instance_ids = updated_vms;
        cluster.status.phase = (cluster.status.available_replicas == cluster.spec.target_replicas) ? "Ready" : "Scaling";

        if (!store_->update(cluster)) {
            std::cout << "  [Status] Помилка CAS при збереженні статусу. Відправка в чергу на повтор..." << std::endl;
            return ReconcileResult{true, std::chrono::milliseconds(200)};
        }

        std::cout << "  [Done] Звірку завершено успішно. Стан узгоджено (Phase=" << cluster.status.phase << ")" << std::endl;
        return ReconcileResult{false};
    }

private:
    std::shared_ptr<ClusterStore> store_;
    std::shared_ptr<CloudProviderDriver> cloud_;
    std::shared_ptr<RateLimitingWorkQueue> queue_;
};
