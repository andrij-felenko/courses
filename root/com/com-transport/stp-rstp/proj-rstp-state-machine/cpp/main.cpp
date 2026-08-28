#include <iostream>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace rstp {

// Строго типізовані переліки (C++11 enum class)
enum class PortRole {
    Disabled,
    Root,
    Designated,
    Alternate,
    Backup
};

enum class PortState {
    Discarding,
    Learning,
    Forwarding
};

// Структура Bridge ID з тристороннім порівнянням (C++20 spaceship operator)
struct BridgeId {
    uint16_t priority{32768};
    std::array<uint8_t, 6> mac{};

    // Автоматичне комбіноване лексикографічне порівняння поля priority, а потім елементів mac
    auto operator<=>(const BridgeId& other) const = default;
};

// Вектор пріоритету BPDU з перевизначеним оператором менше
struct PriorityVector {
    BridgeId root_id{};
    uint32_t root_path_cost{0};
    BridgeId designated_bridge_id{};
    uint16_t designated_port_id{0};

    // Оператор порівняння векторів пріоритетів
    bool operator<(const PriorityVector& other) const noexcept {
        if (root_id != other.root_id) {
            return root_id < other.root_id;
        }
        if (root_path_cost != other.root_path_cost) {
            return root_path_cost < other.root_path_cost;
        }
        if (designated_bridge_id != other.designated_bridge_id) {
            return designated_bridge_id < other.designated_bridge_id;
        }
        return designated_port_id < other.designated_port_id;
    }
};

// Модель кадру BPDU у стилі Modern C++
struct BpduFrame {
    uint16_t protocol_id{0};
    uint8_t version{2};
    uint8_t bpdu_type{2};
    uint8_t flags{0};
    PriorityVector vector{};
    uint16_t message_age{0};
    uint16_t max_age{20};
    uint16_t hello_time{2};
    uint16_t forward_delay{15};
};

// Клас контролера порту (RAII та інкапсуляція стану)
class RstpPortController {
public:
    explicit RstpPortController(uint16_t port_id, BridgeId own_bridge_id)
        : port_id_(port_id), own_bridge_id_(own_bridge_id) {}

    // Обробка вхідного BPDU та оновлення ролі порту
    PortRole evaluate_bpdu(const BpduFrame& bpdu, const PriorityVector& active_vector) noexcept {
        // Якщо вхідний BPDU має вищий пріоритет (bpdu.vector < active_vector)
        if (bpdu.vector < active_vector) {
            if (bpdu.vector.root_id < own_bridge_id_) {
                current_role_ = PortRole::Root;
                current_state_ = PortState::Forwarding; // Миттєве сходження RSTP
            } else {
                current_role_ = PortRole::Alternate;
                current_state_ = PortState::Discarding; // Захист від петлі
            }
        } else {
            current_role_ = PortRole::Designated;
            current_state_ = PortState::Forwarding;
        }
        return current_role_;
    }

    [[nodiscard]] PortRole role() const noexcept { return current_role_; }
    [[nodiscard]] PortState state() const noexcept { return current_state_; }

private:
    uint16_t port_id_;
    BridgeId own_bridge_id_;
    PortRole current_role_{PortRole::Designated};
    PortState current_state_{PortState::Discarding};
};

} // namespace rstp

int main() {
    using namespace rstp;

    BridgeId root_bridge{.priority = 4096, .mac = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55}};
    BridgeId local_bridge{.priority = 32768, .mac = {0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE}};

    RstpPortController port_controller(0x8001, local_bridge);

    PriorityVector current_best{
        .root_id = local_bridge,
        .root_path_cost = 0,
        .designated_bridge_id = local_bridge,
        .designated_port_id = 0x8001
    };

    BpduFrame incoming_bpdu{
        .vector = {
            .root_id = root_bridge,
            .root_path_cost = 4,
            .designated_bridge_id = root_bridge,
            .designated_port_id = 0x8002
        }
    };

    PortRole role = port_controller.evaluate_bpdu(incoming_bpdu, current_best);

    std::cout << "Аналіз RSTP C++20:\n";
    if (role == PortRole::Root) {
        std::cout << "Статус: Роль [Root Port], Стан [Forwarding]\n";
    } else if (role == PortRole::Alternate) {
        std::cout << "Статус: Роль [Alternate Port], Стан [Discarding]\n";
    }

    return 0;
}
