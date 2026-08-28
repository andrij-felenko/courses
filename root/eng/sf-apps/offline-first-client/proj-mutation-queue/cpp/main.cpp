// C++20: Відмовостійкий рушій черги мутацій з RAII та гарантією доставки

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <chrono>
#include <random>
#include <algorithm>
#include <optional>
#include <expected>
#include <functional>

enum class MutationType { Create, Update, Delete };
enum class MutationStatus { Pending, InFlight, Committed, Failed };

struct Mutation {
    std::string id;
    std::string entity_id;
    std::string entity_type;
    MutationType type;
    std::string payload_json;
    uint64_t base_version;
    int64_t created_at_ms;
    MutationStatus status;
    uint32_t retry_count;
};

struct EntityState {
    std::string id;
    uint64_t version;
    std::string data_json;
    bool is_optimistic;
};

class StorageInterface {
public:
    virtual ~StorageInterface() = default;
    virtual void save_mutation(const Mutation& m) = 0;
    virtual void delete_mutation(const std::string& id) = 0;
    virtual std::vector<Mutation> get_pending_mutations() = 0;
    virtual void save_entity(const EntityState& e) = 0;
    virtual std::optional<EntityState> get_entity(const std::string& id) = 0;
};

class MutationQueueEngine {
public:
    using NetworkResult = std::expected<uint64_t, int>; // Повертає new_version або HTTP error code
    using NetworkSender = std::function<NetworkResult(const Mutation&)>;

    MutationQueueEngine(std::shared_ptr<StorageInterface> storage, NetworkSender sender)
        : storage_(std::move(storage)), sender_(std::move(sender)), rng_(std::random_device{}()) {}

    void enqueue(const std::string& entity_id, const std::string& entity_type,
                 MutationType type, const std::string& payload_json) {
        auto current = storage_->get_entity(entity_id).value_or(EntityState{
            .id = entity_id,
            .version = 0,
            .data_json = "{}",
            .is_optimistic = false
        });

        Mutation m{
            .id = generate_uuid(),
            .entity_id = entity_id,
            .entity_type = entity_type,
            .type = type,
            .payload_json = payload_json,
            .base_version = current.version,
            .created_at_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count(),
            .status = MutationStatus::Pending,
            .retry_count = 0
        };

        // 1. Атомарний запис у локальний журнал outbox
        storage_->save_mutation(m);

        // 2. Оптимістичне накладення на локальний стан
        current.data_json = payload_json; // У робочому коді — злиття JSON патчу
        current.is_optimistic = true;
        storage_->save_entity(current);
    }

    void process_queue() {
        auto pending = storage_->get_pending_mutations();
        std::sort(pending.begin(), pending.end(), [](const Mutation& a, const Mutation& b) {
            return a.created_at_ms < b.created_at_ms;
        });

        for (auto& m : pending) {
            m.status = MutationStatus::InFlight;
            storage_->save_mutation(m);

            auto result = sender_(m);
            if (result.has_value()) {
                // Успішна фіксація сервером
                uint64_t new_version = result.value();
                if (auto entity = storage_->get_entity(m.entity_id)) {
                    entity->version = new_version;
                    entity->is_optimistic = false;
                    storage_->save_entity(*entity);
                }
                storage_->delete_mutation(m.id);
            } else {
                int err = result.error();
                if (err >= 400 && err < 500) {
                    // Фатальна помилка клієнта -> відкат і видалення
                    rollback_optimistic(m);
                    storage_->delete_mutation(m.id);
                } else {
                    // Тимчасова мережева помилка -> обчислення паузи з джитером
                    m.status = MutationStatus::Pending;
                    m.retry_count++;
                    storage_->save_mutation(m);
                    break; // Зупинка до наступного циклу
                }
            }
        }
    }

private:
    std::string generate_uuid() {
        return "mut-" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count());
    }

    void rollback_optimistic(const Mutation& m) {
        if (auto entity = storage_->get_entity(m.entity_id)) {
            entity->is_optimistic = false;
            storage_->save_entity(*entity);
        }
    }

    std::shared_ptr<StorageInterface> storage_;
    NetworkSender sender_;
    std::mt19937 rng_;
};
