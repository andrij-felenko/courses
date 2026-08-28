#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_set>
#include <optional>
#include <chrono>
#include <memory>

// Структура валідованої бізнес-події замовлення
struct OrderEvent {
    std::string event_id;
    std::string order_id;
    std::string user_id;
    std::string order_state;
    std::string currency;
    int64_t total_amount_cents{0};
    int64_t tax_amount_cents{0};
    int32_t items_count{0};
    std::string created_at;
};

// Діагностичний конверт для ізоляції бракованих записів у DLQ
struct DlqEnvelope {
    std::string dlq_id;
    std::string failed_at;
    std::string contract_version;
    std::string error_reason;
    std::string raw_payload;
};

// Клас валідатора згідно зі специфікацією контракту
class DataContractValidator {
public:
    explicit DataContractValidator(std::string version)
        : contract_version_(std::move(version)),
          valid_states_{"PENDING", "PAID", "PROCESSING", "SHIPPED", "CANCELLED", "REFUNDED"} {}

    // Повертає std::nullopt у разі успіху або опис помилки
    [[nodiscard]] std::optional<std::string> validate(const OrderEvent& ev) const {
        // 1. Перевірка обов'язкових ідентифікаторів
        if (ev.event_id.empty() || ev.order_id.empty() || ev.user_id.empty()) {
            return "Відсутній обов'язковий ідентифікатор (event_id, order_id або user_id)";
        }

        // 2. Контроль числових меж
        if (ev.total_amount_cents < 0) {
            return "Поле total_amount_cents не може бути від'ємним";
        }
        if (ev.items_count <= 0 || ev.items_count > 500) {
            return "Кількість items_count має бути в діапазоні від 1 до 500";
        }

        // 3. Перевірка скінченного автомата статусів
        if (valid_states_.find(ev.order_state) == valid_states_.end()) {
            return "Недопустимий статус order_state: " + ev.order_state;
        }

        // 4. Перевірка формату валюти ISO-4217
        if (ev.currency.size() != 3) {
            return "Код currency має містити рівно 3 символи ISO-4217";
        }

        // 5. Перевірка семантичного бізнес-інваріанту: tax <= total
        if (ev.tax_amount_cents > ev.total_amount_cents) {
            return "Інваріант порушено: tax_amount_cents перевищує total_amount_cents";
        }

        return std::nullopt; // Валідація пройдена успішно
    }

    [[nodiscard]] const std::string& version() const noexcept { return contract_version_; }

private:
    std::string contract_version_;
    std::unordered_set<std::string> valid_states_;
};

// Шлюз маршрутизації потоку даних
class IngestionGateway {
public:
    explicit IngestionGateway(DataContractValidator validator)
        : validator_(std::move(validator)) {}

    void process(const OrderEvent& ev, const std::string& raw_json) {
        if (auto err = validator_.validate(ev); err.has_value()) {
            dlq_sink_.push_back(DlqEnvelope{
                "dlq-uuid-7f8e-4a",
                "2026-08-20T12:00:00Z",
                validator_.version(),
                *err,
                raw_json
            });
        } else {
            dwh_sink_.push_back(ev);
        }
    }

    [[nodiscard]] size_t dwh_count() const noexcept { return dwh_sink_.size(); }
    [[nodiscard]] size_t dlq_count() const noexcept { return dlq_sink_.size(); }

private:
    DataContractValidator validator_;
    std::vector<OrderEvent> dwh_sink_;
    std::vector<DlqEnvelope> dlq_sink_;
};

int main() {
    DataContractValidator validator("2.3.0");
    IngestionGateway gateway(std::move(validator));

    // Валідна подія від коректного сервісу
    OrderEvent good_event{
        "ev-001", "ord-100", "usr-500", "PAID", "USD", 15000, 3000, 2, "2026-08-20T12:00:00Z"
    };

    // Бракована подія (порушення інваріанту та від'ємна сума)
    OrderEvent bad_event{
        "ev-002", "ord-101", "usr-501", "INVALID_STATUS", "USD", -500, 100, 0, "2026-08-20T12:01:00Z"
    };

    gateway.process(good_event, "{\"raw\":\"good_payload\"}");
    gateway.process(bad_event, "{\"raw\":\"bad_payload\"}");

    std::cout << "Прийнято у DWH: " << gateway.dwh_count() 
              << " | Відправлено в DLQ: " << gateway.dlq_count() << "\n";
    return 0;
}
