// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <memory>
#include <unordered_set>
#include <vector>

struct OrderPlacedEvent {
    std::string event_id;
    std::string order_id;
    double amount;
    std::optional<std::string> tax_identifier; // Опціональне поле для безпечної еволюції
};

class TransactionalOutboxWriter {
public:
    void create_order_with_outbox(std::string_view order_id, double amount, 
                                 std::optional<std::string_view> tax_id) {
        std::cout << "[DB Transaction] BEGIN\n";
        std::cout << "  INSERT INTO orders (id, amount) VALUES ('" << order_id << "', " << amount << ");\n";
        std::cout << "  INSERT INTO outbox (event_type, payload) VALUES ('OrderPlaced', ...);\n";
        std::cout << "[DB Transaction] COMMIT\n";
    }
};

class TolerantEventConsumer {
private:
    mutable std::unordered_set<std::string> processed_event_ids_;

public:
    void process_event(const OrderPlacedEvent& event) const {
        // Перевірка ідемпотентності (захист від дублікатів при деплої)
        if (processed_event_ids_.contains(event.event_id)) {
            std::cout << "[Consumer C++] Duplicate event " << event.event_id << " ignored.\n";
            return;
        }

        std::cout << "[Consumer C++] Event ID: " << event.event_id 
                  << " | Order: " << event.order_id 
                  << " | Amount: " << event.amount << "\n";
        
        if (event.tax_identifier) {
            std::cout << "  -> Tax Identifier: " << *event.tax_identifier << " (V2 Flow)\n";
        } else {
            std::cout << "  -> Tax Identifier: None (Default V1 Fallback Flow)\n";
        }
        
        processed_event_ids_.insert(event.event_id);
        std::cout << "[Consumer C++] Event processed without blocking!\n";
    }
};

int main() {
    TransactionalOutboxWriter outbox;
    TolerantEventConsumer consumer;
    
    std::cout << "--- Phase 1: Producer deploys V2 (Outbox), Consumer is V1 ---\n";
    outbox.create_order_with_outbox("ORD-701", 199.99, std::nullopt);
    consumer.process_event({"EV-01", "ORD-701", 199.99, std::nullopt});
    
    std::cout << "\n--- Phase 2: Consumer updates to V2 ---\n";
    outbox.create_order_with_outbox("ORD-702", 599.00, "TAX-UA-9988");
    consumer.process_event({"EV-02", "ORD-702", 599.00, "TAX-UA-9988"});

    std::cout << "\n--- Phase 3: Retry duplicate event test ---\n";
    consumer.process_event({"EV-02", "ORD-702", 599.00, "TAX-UA-9988"});
    
    return 0;
}
