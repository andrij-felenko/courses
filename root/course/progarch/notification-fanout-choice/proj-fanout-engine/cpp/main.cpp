#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <variant>
#include <span >
#include <chrono>

// Структура сповіщення в Digital Homes
struct NotificationEvent {
    std::string id;
    std::string title;
    std::string body;
    std::string scope_id;        // ID дому, ЖК або глобальної системи
    size_t recipient_count{0};   // Кількість підписників (N)
    bool is_emergency{false};    // Критична тривога (дим, злом, витік)
};

// Результати рішення роутингу
enum class FanOutStrategy {
    FastTrackOnWrite,  // Tier 1: On-Write без злиття, миттєво
    HybridBatched,     // Tier 2: On-Read стрічка + push-батчі
    BroadcastOnRead    // Tier 3: On-Read broadcast feed + topic push
};

struct DispatchDecision {
    FanOutStrategy strategy;
    size_t batch_size;
    std::string route_reason;
};

// Клас трирівневого Fan-Out роутера
class FanOutRouter {
public:
    static constexpr size_t K_MAX_DIRECT_ONWRITE = 10;
    static constexpr size_t K_MAX_COMMUNITY_HYBRID = 5000;
    static constexpr size_t K_PUSH_BATCH_CHUNK = 500;

    [[nodiscard]] DispatchDecision route(const NotificationEvent& event) const noexcept {
        // Критичні тривоги або малоабонентні доми завжди йдуть через Fast-Track On-Write
        if (event.is_emergency || event.recipient_count <= K_MAX_DIRECT_ONWRITE) {
            return {
                FanOutStrategy::FastTrackOnWrite,
                event.recipient_count,
                "Tier 1: Аварійний або локальний доступ (N <= 10). Пряма On-Write розсилка."
            };
        }

        // Середні масиви (будинок, ЖК) — гібридний розсип
        if (event.recipient_count <= K_MAX_COMMUNITY_HYBRID) {
            return {
                FanOutStrategy::HybridBatched,
                K_PUSH_BATCH_CHUNK,
                "Tier 2: Подія ЖК (10 < N <= 5000). On-Read стрічка + push-батчі."
            };
        }

        // Глобальні сповіщення — чистий On-Read + Broadcast Topic
        return {
            FanOutStrategy::BroadcastOnRead,
            1,
            "Tier 3: Системна масова подія (N > 5000). Чистий On-Read + FCM Topic."
        };
    }

    void execute_dispatch(const NotificationEvent& event) const {
        const auto decision = route(event);
        std::cout << "[ROUTER] Подія ID: " << event.id 
                  << " | Стратегія: " << static_cast<int>(decision.strategy)
                  << " | Опис: " << decision.route_reason << "\n";

        switch (decision.strategy) {
            case FanOutStrategy::FastTrackOnWrite:
                dispatch_on_write_fastpath(event);
                break;
            case FanOutStrategy::HybridBatched:
                dispatch_hybrid_community(event, decision.batch_size);
                break;
            case FanOutStrategy::BroadcastOnRead:
                dispatch_broadcast_onread(event);
                break;
        }
    }

private:
    void dispatch_on_write_fastpath(const NotificationEvent& event) const {
        std::cout << "  └─ [Tier 1] Запис " << event.recipient_count 
                  << " персональних inboxes у пам'ять + Push з високим пріоритетом.\n";
    }

    void dispatch_hybrid_community(const NotificationEvent& event, size_t chunk_size) const {
        const size_t num_chunks = (event.recipient_count + chunk_size - 1) / chunk_size;
        std::cout << "  └─ [Tier 2] Збережено 1 запис стрічки ЖК " << event.scope_id 
                  << ". Згенеровано " << num_chunks << " push-батчів по " << chunk_size << " рецепторів.\n";
    }

    void dispatch_broadcast_onread(const NotificationEvent& event) const {
        std::cout << "  └─ [Tier 3] Збережено 1 глобальний запис у системну стрічку. "
                  << "Відправлено 1 multicast push у топік: root://" << event.scope_id << "\n";
    }
};

int main() {
    FanOutRouter router;

    // Сценарій 1: Пожежна тривога в квартирі (2 мешканці)
    NotificationEvent fire_alert{
        "evt-001", "Виявлено дим!", "Датчик у кухні спрацював", "home-1402", 2, true
    };

    // Сценарій 2: Оголошення ОСББ про воду (1200 мешканців ЖК)
    NotificationEvent water_notice{
        "evt-002", "Відключення води", "Завтра з 09:00 ремонтні роботи", "complex-oak", 1200, false
    };

    // Сценарій 3: Оновлення правил сервісу (500 000 користувачів)
    NotificationEvent system_update{
        "evt-003", "Оновлення оферти", "Змінилися умови обслуговування", "global-dh", 500000, false
    };

    router.execute_dispatch(fire_alert);
    router.execute_dispatch(water_notice);
    router.execute_dispatch(system_update);

    return 0;
}
