#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <chrono>
#include <random>
#include <unordered_map>
#include <cstdint>

namespace distributed {

using namespace std::chrono_literals;

enum class MessageType {
    OrderRequest,
    PaymentAck,
    AckToAck
};

struct Packet {
    MessageType type;
    uint64_t order_id;
    uint64_t idempotency_key;
    std::chrono::steady_clock::time_point lease_deadline;
    bool committed{false};
};

/* Клас імітації ненадійного мережевого середовища */
class UnreliableChannel {
public:
    explicit UnreliableChannel(int drop_percentage)
        : drop_rate_(drop_percentage), rng_(1337) {}

    bool transmit(const Packet& pkt, std::string_view from, std::string_view to) {
        std::uniform_int_distribution<int> dist(0, 99);
        if (dist(rng_) < drop_rate_) {
            std::cout << "  [МЕРЕЖА: ВТРАТА] Пакет від " << from << " до " << to << " загублено!\n";
            return false;
        }
        std::cout << "  [МЕРЕЖА: ДОСТАВЛЕНО] Пакет від " << from << " до " << to << " успішно дійшов.\n";
        return true;
    }

private:
    int drop_rate_;
    std::mt19937 rng_;
};

/* Банківський платіжний сервіс із захистом через ідемпотентність та оренди */
class PaymentGateway {
public:
    struct TransactionState {
        bool paid{false};
        std::chrono::steady_clock::time_point lease_expiry;
    };

    std::optional<Packet> handle_request(const Packet& req) {
        auto now = std::chrono::steady_clock::now();
        auto& record = ledger_[req.idempotency_key];

        if (!record.paid) {
            record.paid = true;
            record.lease_expiry = req.lease_deadline;
            std::cout << "  [Банк]: Первинна обробка замовлення #" << req.order_id 
                      << ". Оренда зафіксована.\n";
        } else {
            std::cout << "  [Банк]: Виявлено дублікат запиту (ключ " << req.idempotency_key 
                      << "). Повертаємо збережений статус оплати.\n";
        }

        return Packet{
            .type = MessageType::PaymentAck,
            .order_id = req.order_id,
            .idempotency_key = req.idempotency_key,
            .lease_deadline = record.lease_expiry,
            .committed = true
        };
    }

private:
    std::unordered_map<uint64_t, TransactionState> ledger_;
};

/* Сервіс замовлень із підтримкою повторів та дедлайнів */
class OrderServiceClient {
public:
    OrderServiceClient(UnreliableChannel& channel, PaymentGateway& gateway)
        : channel_(channel), gateway_(gateway) {}

    bool execute_order(uint64_t order_id, uint64_t idempotency_key) {
        constexpr int max_retries = 5;
        constexpr auto lease_time = 500ms;

        for (int attempt = 1; attempt <= max_retries; ++attempt) {
            auto now = std::chrono::steady_clock::now();
            auto deadline = now + lease_time;

            std::cout << "Спроба #" << attempt << ": Відправка запиту на оплату замовлення #" 
                      << order_id << "...\n";

            Packet req{
                .type = MessageType::OrderRequest,
                .order_id = order_id,
                .idempotency_key = idempotency_key,
                .lease_deadline = deadline,
                .committed = false
            };

            if (channel_.transmit(req, "Магазин", "Банк")) {
                auto response = gateway_.handle_request(req);
                if (response.has_value() && channel_.transmit(*response, "Банк", "Магазин")) {
                    std::cout << "  [Магазин]: Отримано успішне підтвердження! Замовлення видано клієнту.\n";
                    return true;
                }
                std::cout << "  [Магазин]: Зворотний ACK втрачено. Очікування таймауту перед повтором...\n";
            } else {
                std::cout << "  [Магазин]: Запит втрачено в дорозі. Очікування таймауту...\n";
            }
        }
        std::cout << "  [Магазин]: Вичерпано ліміт спроб. Запуск компенсаційної саги.\n";
        return false;
    }

private:
    UnreliableChannel& channel_;
    PaymentGateway& gateway_;
};

} // namespace distributed

int main() {
    std::cout << "Симуляція інженерного протоколу на базі оренди та ідемпотентності (C++20)\n";
    
    distributed::UnreliableChannel network(30); // 30% втрат пакетів
    distributed::PaymentGateway bank;
    distributed::OrderServiceClient store(network, bank);

    bool result = store.execute_order(4001, 0xABCDEF123456ULL);
    
    std::cout << "\nФінальний статус операції: " << (result ? "УСПІХ (COMMIT)" : "ВІДХИЛЕНО (ABORT)") << "\n";
    return 0;
}
