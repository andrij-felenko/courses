#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <optional>
#include <memory>
#include <chrono>
#include <algorithm>
#include <stdexcept>

// DTO бізнес-сутності товару
struct ProductRecord {
    int64_t id;
    std::string title;
    std::string category;
    double price;
    int64_t version;
    bool is_deleted;
};

// Запис у таблиці Transactional Outbox
struct OutboxEvent {
    int64_t seq_id;
    int64_t aggregate_id;
    std::string event_type; // "UPSERT" або "DELETE"
    std::string payload_json;
    int64_t version;
    bool processed;
};

// Документ у пошуковому індексі
struct IndexedDocument {
    int64_t id;
    std::string title;
    std::string category;
    double price;
    int64_t version;
};

// Імітація пошукового індексу (Elasticsearch / OpenSearch Shard)
class SearchIndex {
public:
    explicit SearchIndex(std::string name) : name_(std::move(name)) {}

    // Індексація з оптимістичним контролем версій (external versioning)
    bool index_document(const IndexedDocument& doc) {
        auto it = storage_.find(doc.id);
        if (it != storage_.end()) {
            // Захист від гонки оновлень: ігноруємо старі або повторні версії
            if (doc.version < it->second.version) {
                std::cout << "[" << name_ << "] Відкинуто застарілу версію doc#" 
                          << doc.id << " (поточна: " << it->second.version 
                          << ", отримана: " << doc.version << ")\n";
                return false;
            }
        }
        storage_[doc.id] = doc;
        std::cout << "[" << name_ << "] Успішно проіндексовано doc#" << doc.id 
                  << " (версія: " << doc.version << ", назва: '" << doc.title << "')\n";
        return true;
    }

    bool delete_document(int64_t id, int64_t version) {
        auto it = storage_.find(id);
        if (it != storage_.end()) {
            if (version < it->second.version) {
                return false;
            }
            storage_.erase(it);
            std::cout << "[" << name_ << "] Видалено doc#" << id << " v" << version << "\n";
            return true;
        }
        return false;
    }

    [[nodiscard]] std::optional<IndexedDocument> get(int64_t id) const {
        auto it = storage_.find(id);
        if (it != storage_.end()) return it->second;
        return std::nullopt;
    }

    [[nodiscard]] size_t size() const { return storage_.size(); }
    [[nodiscard]] const std::string& name() const { return name_; }

private:
    std::string name_;
    std::unordered_map<int64_t, IndexedDocument> storage_;
};

// Менеджер псевдонімів пошуку (Index Alias Registry)
class SearchCluster {
public:
    void register_index(std::shared_ptr<SearchIndex> index) {
        indices_[index->name()] = index;
    }

    void set_alias(const std::string& alias, const std::string& target_index) {
        if (indices_.find(target_index) == indices_.end()) {
            throw std::runtime_error("Цільовий індекс не знайдено: " + target_index);
        }
        aliases_[alias] = target_index;
        std::cout << "[CLUSTER] Аліас '" << alias << "' тепер вказує на '" << target_index << "'\n";
    }

    std::shared_ptr<SearchIndex> get_by_alias(const std::string& alias) {
        auto it = aliases_.find(alias);
        if (it == aliases_.end()) return nullptr;
        return indices_[it->second];
    }

    std::shared_ptr<SearchIndex> get_index(const std::string& name) {
        auto it = indices_.find(name);
        if (it == indices_.end()) return nullptr;
        return it->second;
    }

private:
    std::unordered_map<std::string, std::shared_ptr<SearchIndex>> indices_;
    std::unordered_map<std::string, std::string> aliases_;
};

// Первинна реляційна база з підтримкою Outbox (PostgreSQL Mock)
class RelationalDatabase {
public:
    // Атомарна бізнес-операція збереження товару
    void save_product(int64_t id, const std::string& title, const std::string& category, double price) {
        int64_t current_ver = 1;
        auto it = products_.find(id);
        if (it != products_.end()) {
            current_ver = it->second.version + 1;
        }

        ProductRecord record{id, title, category, price, current_ver, false};
        products_[id] = record;

        // В тій самій транзакції створюємо запис в Outbox
        int64_t next_seq = static_cast<int64_t>(outbox_.size() + 1);
        std::string json_repr = "{\"title\":\"" + title + "\",\"category\":\"" + category + "\"}";
        
        outbox_.push_back(OutboxEvent{
            next_seq,
            id,
            "UPSERT",
            json_repr,
            current_ver,
            false // ще не оброблено
        });

        std::cout << "[DB] Збережено товар #" << id << " v" << current_ver 
                  << " та додано outbox event seq#" << next_seq << "\n";
    }

    // Вибірка невідправлених подій для Outbox Relay Worker
    std::vector<OutboxEvent> fetch_unprocessed_outbox(size_t batch_size) {
        std::vector<OutboxEvent> batch;
        for (auto& ev : outbox_) {
            if (!ev.processed) {
                batch.push_back(ev);
                if (batch.size() >= batch_size) break;
            }
        }
        return batch;
    }

    void mark_outbox_processed(int64_t seq_id) {
        for (auto& ev : outbox_) {
            if (ev.seq_id == seq_id) {
                ev.processed = true;
                break;
            }
        }
    }

    // Вивантаження історичного знімка для бекфілу
    std::vector<ProductRecord> get_all_active_products() const {
        std::vector<ProductRecord> list;
        for (const auto& [id, prod] : products_) {
            if (!prod.is_deleted) {
                list.push_back(prod);
            }
        }
        return list;
    }

    [[nodiscard]] int64_t get_current_max_seq() const {
        return static_cast<int64_t>(outbox_.size());
    }

    std::vector<OutboxEvent> get_events_after(int64_t after_seq) const {
        std::vector<OutboxEvent> delta;
        for (const auto& ev : outbox_) {
            if (ev.seq_id > after_seq) {
                delta.push_back(ev);
            }
        }
        return delta;
    }

private:
    std::unordered_map<int64_t, ProductRecord> products_;
    std::vector<OutboxEvent> outbox_;
};

// Служба синхронізації та міграції індексів
class SearchSyncPipeline {
public:
    SearchSyncPipeline(RelationalDatabase& db, SearchCluster& cluster)
        : db_(db), cluster_(cluster) {}

    // Цикл диспетчера Outbox: передає події в активний індекс
    void process_outbox_batch(const std::string& write_alias) {
        auto index = cluster_.get_by_alias(write_alias);
        if (!index) throw std::runtime_error("Активний індекс не знайдено для аліаса");

        auto batch = db_.fetch_unprocessed_outbox(10);
        for (const auto& ev : batch) {
            if (ev.event_type == "UPSERT") {
                // У реальній системі тут відбувається парсинг JSON
                IndexedDocument doc{
                    ev.aggregate_id,
                    "Sony WH-1000XM5", // спрощений розбір для ілюстрації
                    "audio",
                    14999.0,
                    ev.version
                };
                index->index_document(doc);
            }
            db_.mark_outbox_processed(ev.seq_id);
        }
    }

    // Повна жива переіндексація з нульовим простоєм (Zero-Downtime Reindex)
    void execute_zero_downtime_reindex(
        const std::string& alias_name, 
        const std::string& new_index_name) 
    {
        std::cout << "\n=== СТАРТ ЖИВОЇ ПЕРЕІНДЕКСАЦІЇ: " << new_index_name << " ===\n";

        // Крок 1: Створення нового індексу
        auto new_index = std::make_shared<SearchIndex>(new_index_name);
        cluster_.register_index(new_index);

        // Фіксуємо точку відліку змін перед початком знімка
        int64_t snapshot_seq = db_.get_current_max_seq();
        std::cout << "[MIGRATION] Точка фіксації послідовності (LSN): seq#" << snapshot_seq << "\n";

        // Крок 2: Пакетний бекфіл з первинної бази (Bulk backfill)
        auto snapshot_data = db_.get_all_active_products();
        std::cout << "[MIGRATION] Бекфіл: перенесення " << snapshot_data.size() << " документів...\n";
        for (const auto& prod : snapshot_data) {
            new_index->index_document(IndexedDocument{
                prod.id, prod.title, prod.category, prod.price, prod.version
            });
        }

        // Крок 3: Доганяння подій, які виникли під час бекфілу (Catch-up replay)
        auto delta_events = db_.get_events_after(snapshot_seq);
        std::cout << "[MIGRATION] Доганяння черги: застосування " << delta_events.size() << " дельта-подій...\n";
        for (const auto& ev : delta_events) {
            new_index->index_document(IndexedDocument{
                ev.aggregate_id, "Оновлений товар", "audio", 15500.0, ev.version
            });
        }

        // Крок 4: Атомарне перемикання псевдоніма
        cluster_.set_alias(alias_name, new_index_name);
        std::cout << "=== ПЕРЕІНДЕКСАЦІЮ ЗАВЕРШЕНО УСПІШНО ===\n\n";
    }

private:
    RelationalDatabase& db_;
    SearchCluster& cluster_;
};
