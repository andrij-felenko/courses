#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <optional>
#include <expected>
#include <memory>

enum class NodeKind {
    Symptom,
    Check,
    Action
};

struct DiagnosticNode {
    uint32_t id;
    NodeKind kind;
    std::string description;
    std::optional<uint32_t> next_pass_id;
    std::optional<uint32_t> next_fail_id;
};

class DiagnosticGraph {
public:
    void add_node(uint32_t id, NodeKind kind, std::string_view desc,
                  std::optional<uint32_t> pass_id = std::nullopt,
                  std::optional<uint32_t> fail_id = std::nullopt) {
        nodes_[id] = DiagnosticNode{
            .id = id,
            .kind = kind,
            .description = std::string(desc),
            .next_pass_id = pass_id,
            .next_fail_id = fail_id
        };
    }

    [[nodiscard]] std::expected<void, std::string> validate() const {
        if (nodes_.empty()) {
            return std::unexpected("Граф порожній: немає зареєстрованих станів");
        }

        for (const auto& [id, node] : nodes_) {
            if (node.kind == NodeKind::Symptom) {
                std::unordered_set<uint32_t> visited;
                auto res = check_reachability(node, visited);
                if (!res) {
                    return std::unexpected("Симптом [ID " + std::to_string(id) + 
                                           ": " + node.description + "] має дефект: " + res.error());
                }
            }
        }
        return {};
    }

    void execute_interactive(uint32_t symptom_id, const std::vector<bool>& simulated_answers = {}) const {
        auto it = nodes_.find(symptom_id);
        if (it == nodes_.end() || it->second.kind != NodeKind::Symptom) {
            std::cout << "[ПОМИЛКА] Вхідний симптом не знайдено.\n";
            return;
        }

        std::cout << "\n=== СЕАНС ДІАГНОСТИКИ (C++20 Engine) ===\n";
        std::cout << "[СИМПТОМ] ID " << it->second.id << ": " << it->second.description << "\n";

        if (!it->second.next_pass_id) return;
        uint32_t current_id = *it->second.next_pass_id;
        size_t answer_idx = 0;

        while (nodes_.contains(current_id)) {
            const auto& current = nodes_.at(current_id);
            if (current.kind == NodeKind::Check) {
                std::cout << "\n[ПЕРЕВІРКА ID " << current.id << "]: " << current.description << "\n";
                bool answer = false;
                if (answer_idx < simulated_answers.size()) {
                    answer = simulated_answers[answer_idx++];
                    std::cout << "Результат тесту (симуляція): " << (answer ? "ТАК / PASS" : "НІ / FAIL") << "\n";
                } else {
                    std::cout << "Результат тесту (за замовчуванням): НІ / FAIL\n";
                }

                if (answer) {
                    if (!current.next_pass_id) break;
                    current_id = *current.next_pass_id;
                } else {
                    if (!current.next_fail_id) break;
                    current_id = *current.next_fail_id;
                }
            } else if (current.kind == NodeKind::Action) {
                std::cout << "\n[ВІДНОВЛЮВАЛЬНА ДІЯ ID " << current.id << "]:\n-> "
                          << current.description << "\n";
                std::cout << "=== ВІДНОВЛЕННЯ ЗАВЕРШЕНО ===\n";
                break;
            } else {
                break;
            }
        }
    }

private:
    std::unordered_map<uint32_t, DiagnosticNode> nodes_;

    [[nodiscard]] std::expected<void, std::string> check_reachability(
        const DiagnosticNode& node, std::unordered_set<uint32_t>& visited) const {
        
        if (node.kind == NodeKind::Action) {
            return {};
        }

        if (visited.contains(node.id)) {
            return std::unexpected("Виявлено циклічну залежність у вузлі ID " + std::to_string(node.id));
        }
        visited.insert(node.id);

        if (node.kind == NodeKind::Symptom) {
            if (!node.next_pass_id || !nodes_.contains(*node.next_pass_id)) {
                return std::unexpected("Симптом не має вихідного переходу до перевірки");
            }
            auto res = check_reachability(nodes_.at(*node.next_pass_id), visited);
            visited.erase(node.id);
            return res;
        }

        if (node.kind == NodeKind::Check) {
            if (!node.next_pass_id || !nodes_.contains(*node.next_pass_id)) {
                return std::unexpected("Вузол перевірки ID " + std::to_string(node.id) + " не має гілки PASS");
            }
            if (!node.next_fail_id || !nodes_.contains(*node.next_fail_id)) {
                return std::unexpected("Вузол перевірки ID " + std::to_string(node.id) + " не має гілки FAIL");
            }

            auto visited_pass = visited;
            auto pass_res = check_reachability(nodes_.at(*node.next_pass_id), visited_pass);
            if (!pass_res) return pass_res;

            auto visited_fail = visited;
            auto fail_res = check_reachability(nodes_.at(*node.next_fail_id), visited_fail);
            if (!fail_res) return fail_res;

            visited.erase(node.id);
            return {};
        }

        visited.erase(node.id);
        return std::unexpected("Невідомий тип вузла");
    }
};

int main() {
    DiagnosticGraph diag;

    /* Створення вузлів графа діагностики промислового контролера */
    diag.add_node(1, NodeKind::Symptom, "Червоний світлодіод STATUS блимає кожні 2 с", 2);
    diag.add_node(2, NodeKind::Check, "Напруга живлення V+ у межах 18..30 В DC?", 3, 101);
    diag.add_node(101, NodeKind::Action, "Замінити запобіжник 24 В та перевірити блок живлення");
    diag.add_node(3, NodeKind::Check, "Термінація RS-485 на шині дорівнює 60 Ом?", 4, 102);
    diag.add_node(102, NodeKind::Action, "Увімкнути термінатор 120 Ом на кінцевих вузлах");
    diag.add_node(4, NodeKind::Action, "Перевірити унікальність Modbus ID та швидкість зв'язку");

    auto validation = diag.validate();
    if (validation) {
        std::cout << "[ВАЛІДАЦІЯ] Граф перевірено успішно: усі шляхи досягають відновлювальних дій.\n";
        diag.execute_interactive(1, {true, false});
    } else {
        std::cout << "[ПОМИЛКА ВАЛІДАЦІЇ] " << validation.error() << "\n";
    }

    return 0;
}
