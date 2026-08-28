#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <unordered_map>
#include <memory>
#include <optional>
#include <chrono>
#include <algorithm>
#include <mutex>
#include <cstdint>
#include <sstream>

// ── Векторний годинник (Vector Clock) ───────────────────────────────────────
enum class ClockRelation {
    Equal,      // V_A == V_B
    Ancestor,   // V_A < V_B (A строго передує B)
    Descendant, // V_A > V_B (A строго новіший за B)
    Concurrent  // V_A || V_B (Конкурентні оновлення / Конфлікт)
};

class VectorClock {
private:
    std::map<std::string, uint64_t> versions_;

public:
    VectorClock() = default;

    void increment(const std::string& node_id) {
        versions_[node_id]++;
    }

    uint64_t get(const std::string& node_id) const {
        auto it = versions_.find(node_id);
        return (it != versions_.end()) ? it->second : 0;
    }

    const std::map<std::string, uint64_t>& entries() const {
        return versions_;
    }

    // Злиття векторів: покомпонентний максимум (напівґратка)
    VectorClock merge(const VectorClock& other) const {
        VectorClock result = *this;
        for (const auto& [node, ver] : other.versions_) {
            result.versions_[node] = std::max(result.get(node), ver);
        }
        return result;
    }

    // Порівняння часткового порядку двох векторних годинників
    ClockRelation compare(const VectorClock& other) const {
        bool has_greater = false;
        bool has_less = false;

        // Збираємо всі унікальні ідентифікатори вузлів
        std::map<std::string, uint64_t> all_nodes = versions_;
        for (const auto& [node, ver] : other.versions_) {
            all_nodes[node] = std::max(all_nodes[node], ver);
        }

        for (const auto& [node, _] : all_nodes) {
            uint64_t v1 = get(node);
            uint64_t v2 = other.get(node);

            if (v1 > v2) has_greater = true;
            if (v1 < v2) has_less = true;
        }

        if (!has_greater && !has_less) return ClockRelation::Equal;
        if (has_greater && !has_less)  return ClockRelation::Descendant;
        if (!has_greater && has_less)  return ClockRelation::Ancestor;
        return ClockRelation::Concurrent;
    }

    std::string to_string() const {
        std::ostringstream oss;
        oss << "{";
        bool first = true;
        for (const auto& [node, ver] : versions_) {
            if (!first) oss << ", ";
            oss << node << ":" << ver;
            first = false;
        }
        oss << "}";
        return oss.str();
    }
};

// ── Значення з метаданими версіонування ─────────────────────────────────────
struct VersionedValue {
    std::string key;
    std::string value;
    VectorClock clock;
    int64_t timestamp_ms{0};
    bool is_tombstone{false};

    // Детерміноване злиття двох конкурентних версій
    static VersionedValue merge_concurrent(const VersionedValue& a, const VersionedValue& b) {
        VersionedValue merged;
        merged.key = a.key;
        merged.clock = a.clock.merge(b.clock);

        // Правило розв'язання конфлікту: пріоритет LWW за фізичним часом
        // При рівності фізичного часу — детермінований лексикографічний вибір
        if (a.timestamp_ms > b.timestamp_ms) {
            merged.value = a.value;
            merged.timestamp_ms = a.timestamp_ms;
            merged.is_tombstone = a.is_tombstone;
        } else if (b.timestamp_ms > a.timestamp_ms) {
            merged.value = b.value;
            merged.timestamp_ms = b.timestamp_ms;
            merged.is_tombstone = b.is_tombstone;
        } else {
            merged.value = std::max(a.value, b.value);
            merged.timestamp_ms = a.timestamp_ms;
            merged.is_tombstone = a.is_tombstone || b.is_tombstone;
        }
        return merged;
    }
};

// ── Вузол кластера (Storage Node) ──────────────────────────────────────────
class StorageNode {
private:
    std::string node_id_;
    std::unordered_map<std::string, VersionedValue> store_;
    mutable std::mutex mutex_;

public:
    explicit StorageNode(std::string node_id) : node_id_(std::move(node_id)) {}

    const std::string& id() const { return node_id_; }

    // Локальний запис із просуванням годинника вузла
    VersionedValue put_local(const std::string& key, const std::string& value,
                             const VectorClock& client_clock, int64_t timestamp_ms) {
        std::lock_guard<std::mutex> lock(mutex_);

        VectorClock new_clock = client_clock;
        new_clock.increment(node_id_);

        VersionedValue entry{
            .key = key,
            .value = value,
            .clock = new_clock,
            .timestamp_ms = timestamp_ms,
            .is_tombstone = false
        };

        store_[key] = entry;
        return entry;
    }

    // Прийом репліки від іншого вузла (із перевіркою часткового порядку)
    bool apply_replication(const VersionedValue& incoming) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(incoming.key);

        if (it == store_.end()) {
            store_[incoming.key] = incoming;
            return true;
        }

        ClockRelation rel = incoming.clock.compare(it->second.clock);

        if (rel == ClockRelation::Descendant) {
            // Вхідний запис строго новіший — заміщуємо старий
            it->second = incoming;
            return true;
        } else if (rel == ClockRelation::Concurrent) {
            // Конкурентний запис — виконуємо детерміноване злиття
            it->second = VersionedValue::merge_concurrent(it->second, incoming);
            return true;
        }
        // Вхідний запис є предком (застарілий) — відхиляємо
        return false;
    }

    std::optional<VersionedValue> get_local(const std::string& key) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(key);
        if (it != store_.end() && !it->second.is_tombstone) {
            return it->second;
        }
        return std::nullopt;
    }

    std::unordered_map<std::string, VersionedValue> get_all_entries() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return store_;
    }
};

// ── Кластерний координатор з підтримкою Read-Repair ────────────────────────
class DistributedCluster {
private:
    std::vector<std::shared_ptr<StorageNode>> nodes_;

public:
    void add_node(std::shared_ptr<StorageNode> node) {
        nodes_.push_back(std::move(node));
    }

    std::shared_ptr<StorageNode> get_node(const std::string& id) {
        for (auto& n : nodes_) {
            if (n->id() == id) return n;
        }
        return nullptr;
    }

    // Читання з кворуму з реактивним виправленням (Read-Repair)
    std::optional<VersionedValue> read_with_repair(const std::string& key,
                                                   const std::vector<std::string>& node_ids) {
        std::vector<VersionedValue> responses;
        std::vector<std::shared_ptr<StorageNode>> participating_nodes;

        for (const auto& nid : node_ids) {
            auto node = get_node(nid);
            if (!node) continue;
            participating_nodes.push_back(node);
            auto val = node->get_local(key);
            if (val.has_value()) {
                responses.push_back(*val);
            }
        }

        if (responses.empty()) return std::nullopt;

        // Знаходимо найсвіжішу або зведену версію
        VersionedValue canonical = responses[0];
        for (size_t i = 1; i < responses.size(); ++i) {
            ClockRelation rel = canonical.clock.compare(responses[i].clock);
            if (rel == ClockRelation::Ancestor) {
                canonical = responses[i];
            } else if (rel == ClockRelation::Concurrent) {
                canonical = VersionedValue::merge_concurrent(canonical, responses[i]);
            }
        }

        // Read-Repair: надсилаємо оновлений канонічний стан усім відсталим вузлам
        for (auto& node : participating_nodes) {
            auto current = node->get_local(key);
            if (!current.has_value() ||
                current->clock.compare(canonical.clock) == ClockRelation::Ancestor) {
                std::cout << "  [Read-Repair] Вузол " << node->id()
                          << " оновлено до годинника " << canonical.clock.to_string() << "\n";
                node->apply_replication(canonical);
            }
        }

        return canonical;
    }

    // Фонова анти-ентропія між двома вузлами (Gossip Sync)
    void anti_entropy_sync(const std::string& node_a_id, const std::string& node_b_id) {
        auto node_a = get_node(node_a_id);
        auto node_b = get_node(node_b_id);
        if (!node_a || !node_b) return;

        auto entries_a = node_a->get_all_entries();
        auto entries_b = node_b->get_all_entries();

        for (const auto& [k, v_a] : entries_a) {
            node_b->apply_replication(v_a);
        }
        for (const auto& [k, v_b] : entries_b) {
            node_a->apply_replication(v_b);
        }
    }
};

// ── Клієнтська сесія з гарантією Read-Your-Writes ────────────────────────────
class ClientSession {
private:
    std::string client_id_;
    DistributedCluster& cluster_;
    VectorClock session_clock_; // Токен причинності клієнта

public:
    ClientSession(std::string client_id, DistributedCluster& cluster)
        : client_id_(std::move(client_id)), cluster_(cluster) {}

    void write(const std::string& preferred_node, const std::string& key,
               const std::string& value, int64_t timestamp_ms) {
        auto node = cluster_.get_node(preferred_node);
        if (!node) throw std::runtime_error("Node not found");

        VersionedValue result = node->put_local(key, value, session_clock_, timestamp_ms);
        // Оновлюємо клієнтський токен версії
        session_clock_ = session_clock_.merge(result.clock);

        std::cout << "[Client " << client_id_ << " Write] Ключ: " << key
                  << " -> " << preferred_node << ", новий токен: "
                  << session_clock_.to_string() << "\n";
    }

    // Читання з перевіркою сесійного інваріанта
    std::optional<std::string> read_with_session_guarantee(const std::string& target_node,
                                                           const std::string& key) {
        auto node = cluster_.get_node(target_node);
        if (!node) return std::nullopt;

        auto val = node->get_local(key);

        // Перевіряємо, чи вузол уже наздогнав власний запис клієнта
        if (val.has_value()) {
            ClockRelation rel = val->clock.compare(session_clock_);
            if (rel == ClockRelation::Ancestor) {
                std::cout << "  [Попередження] Вузол " << target_node
                          << " відстає від сесії клієнта! Потрібен Read-Repair.\n";
            }
        }

        // Якщо вузол відстає — ініціюємо читання з виправленням по кластеру
        auto repaired = cluster_.read_with_repair(key, {"Node-EU", "Node-US"});
        if (repaired.has_value()) {
            session_clock_ = session_clock_.merge(repaired->clock);
            return repaired->value;
        }
        return std::nullopt;
    }
};

int main() {
    DistributedCluster cluster;
    auto node_eu = std::make_shared<StorageNode>("Node-EU");
    auto node_us = std::make_shared<StorageNode>("Node-US");

    cluster.add_node(node_eu);
    cluster.add_node(node_us);

    std::cout << "=== 1. Одночасні записи в ізольовані регіони (Мережевий поділ) ===\n";
    ClientSession client_alice("Alice", cluster);
    ClientSession client_bob("Bob", cluster);

    // Аліса пише в Регіон EU, Боб пише в Регіон US одночасно
    client_alice.write("Node-EU", "config:theme", "dark-mode", 1000);
    client_bob.write("Node-US", "config:theme", "light-mode", 1005);

    std::cout << "\n=== 2. Стан вузлів до синхронізації ===\n";
    auto val_eu = node_eu->get_local("config:theme");
    auto val_us = node_us->get_local("config:theme");
    std::cout << "Node-EU стан: " << (val_eu ? val_eu->value : "null")
              << " | годинник: " << val_eu->clock.to_string() << "\n";
    std::cout << "Node-US стан: " << (val_us ? val_us->value : "null")
              << " | годинник: " << val_us->clock.to_string() << "\n";

    std::cout << "\n=== 3. Аліса читає з Node-US (Сесійний захист + Read-Repair) ===\n";
    auto res_alice = client_alice.read_with_session_guarantee("Node-US", "config:theme");
    std::cout << "Аліса отримала зведений результат: " << (res_alice ? *res_alice : "null") << "\n";

    std::cout << "\n=== 4. Фонова синхронізація Anti-Entropy (Повна збіжність) ===\n";
    cluster.anti_entropy_sync("Node-EU", "Node-US");

    auto final_eu = node_eu->get_local("config:theme");
    auto final_us = node_us->get_local("config:theme");
    std::cout << "Node-EU фінал: " << final_eu->value << " | " << final_eu->clock.to_string() << "\n";
    std::cout << "Node-US фінал: " << final_us->value << " | " << final_us->clock.to_string() << "\n";

    return 0;
}
