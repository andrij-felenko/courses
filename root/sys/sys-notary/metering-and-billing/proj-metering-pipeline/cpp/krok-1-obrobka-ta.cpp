#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <cstdint>
#include <chrono>
#include <vector>
#include <unordered_set>
#include <iomanip>
#include <sstream>

// Фіксована точність: 1 USD = 1 000 000 мікродоларів
using CurrencyMicros = int64_t;

struct UsageEvent {
    std::string event_id;
    std::string idempotency_key;
    std::string tenant_id;
    std::string metric_name;
    uint64_t quantity;
    std::chrono::system_clock::time_point occurred_at;
};

enum class IngestResult {
    Accepted,
    DuplicateIgnored,
    InvalidData
};

class EventIngestEngine {
private:
    // У продакшені це первинний унікальний індекс бази даних або Redis Bloom-фільтр
    std::unordered_set<std::string> seen_idempotency_keys_;

public:
    IngestResult ingest_event(const UsageEvent& event) {
        if (event.tenant_id.empty() || event.metric_name.empty() || event.quantity == 0) {
            return IngestResult::InvalidData;
        }

        // Атомарна перевірка та додавання ключа ідемпотентності
        auto [it, inserted] = seen_idempotency_keys_.insert(event.idempotency_key);
        if (!inserted) {
            // Подію вже було прийнято й зафіксовано раніше — мовчки ігноруємо повтор
            return IngestResult::DuplicateIgnored;
        }

        return IngestResult::Accepted;
    }
};
