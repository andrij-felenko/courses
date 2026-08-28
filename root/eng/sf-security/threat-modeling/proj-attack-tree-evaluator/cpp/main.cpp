#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <numeric>
#include <algorithm>
#include <iomanip>
#include <limits>

enum class NodeType {
    Leaf,
    Or,
    And
};

struct DreadScore {
    double damage{0.0};
    double reproducibility{0.0};
    double exploitability{0.0};
    double affected_users{0.0};
    double discoverability{0.0};

    [[nodiscard]] double total() const noexcept {
        return (damage + reproducibility + exploitability + affected_users + discoverability) / 5.0;
    }
};

class AttackNode {
public:
    std::string name;
    NodeType type;
    double cost{0.0};
    double probability{0.0};
    int skill_level{0};
    DreadScore dread{};
    std::vector<std::unique_ptr<AttackNode>> children;

    AttackNode(std::string node_name, NodeType node_type, double c = 0.0, double p = 0.0,
               int skill = 0, DreadScore d = {})
        : name(std::move(node_name)), type(node_type), cost(c), probability(p),
          skill_level(skill), dread(d) {}

    void add_child(std::unique_ptr<AttackNode> child) {
        children.push_back(std::move(child));
    }

    void evaluate() {
        for (const auto& child : children) {
            child->evaluate();
        }

        if (type == NodeType::Leaf || children.empty()) {
            return;
        }

        if (type == NodeType::Or) {
            cost = std::numeric_limits<double>::max();
            double prod_inv_p = 1.0;
            skill_level = std::numeric_limits<int>::max();
            double max_dread_val = -1.0;

            for (const auto& child : children) {
                cost = std::min(cost, child->cost);
                prod_inv_p *= (1.0 - child->probability);
                skill_level = std::min(skill_level, child->skill_level);
                if (child->dread.total() > max_dread_val) {
                    max_dread_val = child->dread.total();
                    dread = child->dread;
                }
            }
            probability = 1.0 - prod_inv_p;
        } else if (type == NodeType::And) {
            cost = 0.0;
            probability = 1.0;
            skill_level = 0;
            DreadScore sum_dread{};

            for (const auto& child : children) {
                cost += child->cost;
                probability *= child->probability;
                skill_level = std::max(skill_level, child->skill_level);
                sum_dread.damage += child->dread.damage;
                sum_dread.reproducibility += child->dread.reproducibility;
                sum_dread.exploitability += child->dread.exploitability;
                sum_dread.affected_users += child->dread.affected_users;
                sum_dread.discoverability += child->dread.discoverability;
            }

            const double n = static_cast<double>(children.size());
            dread = DreadScore{
                sum_dread.damage / n,
                sum_dread.reproducibility / n,
                sum_dread.exploitability / n,
                sum_dread.affected_users / n,
                sum_dread.discoverability / n
            };
        }
    }

    void print_report(int indent = 0) const {
        const std::string pad(indent * 2, ' ');
        const char* type_label = type == NodeType::Leaf ? "LEAF" : (type == NodeType::Or ? "OR" : "AND");
        std::cout << pad << "[" << type_label << "] " << name
                  << " | Cost: " << std::fixed << std::setprecision(0) << cost << " грн"
                  << " | Prob: " << std::setprecision(4) << probability
                  << " (" << std::setprecision(2) << probability * 100.0 << "%)"
                  << " | Skill: " << skill_level
                  << " | DREAD: " << std::setprecision(1) << dread.total() << "/10\n";

        for (const auto& child : children) {
            child->print_report(indent + 1);
        }
    }
};

int main() {
    auto root = std::make_unique<AttackNode>("Злам платіжного шлюзу", NodeType::Or);

    auto branch1 = std::make_unique<AttackNode>("API підробка", NodeType::And);
    branch1->add_child(std::make_unique<AttackNode>("Фішинг API-ключа", NodeType::Leaf, 25000.0, 0.20, 2, DreadScore{8.0, 7.0, 6.0, 9.0, 5.0}));
    branch1->add_child(std::make_unique<AttackNode>("BGP/IP spoofing", NodeType::Leaf, 15000.0, 0.30, 3, DreadScore{6.0, 8.0, 5.0, 4.0, 7.0}));

    auto branch2 = std::make_unique<AttackNode>("SQL-ін'єкція", NodeType::And);
    branch2->add_child(std::make_unique<AttackNode>("Виявлення SQLi", NodeType::Leaf, 10000.0, 0.10, 2, DreadScore{9.0, 9.0, 8.0, 10.0, 6.0}));
    branch2->add_child(std::make_unique<AttackNode>("Обхід WAF", NodeType::Leaf, 20000.0, 0.25, 3, DreadScore{7.0, 6.0, 5.0, 8.0, 4.0}));

    root->add_child(std::move(branch1));
    root->add_child(std::move(branch2));

    root->evaluate();
    root->print_report();

    return 0;
}
