#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <algorithm>

// Типи вузлів
enum class NodeType { VAR, AND, OR, NOT };

// Абстрактне синтаксичне дерево
struct Node {
    NodeType type;
    std::string name;
    std::shared_ptr<Node> left, right;

    Node(std::string n) : type(NodeType::VAR), name(std::move(n)) {}
    Node(NodeType t, std::shared_ptr<Node> l, std::shared_ptr<Node> r = nullptr)
        : type(t), left(std::move(l)), right(std::move(r)) {}
};

// Секвенція
struct Sequent {
    std::vector<std::shared_ptr<Node>> left;
    std::vector<std::shared_ptr<Node>> right;
};

// Допоміжна перевірка на аксіому (спільна змінна)
bool isAxiom(const Sequent& seq) {
    for (const auto& l : seq.left) {
        if (l->type == NodeType::VAR) {
            for (const auto& r : seq.right) {
                if (r->type == NodeType::VAR && l->name == r->name) {
                    return true;
                }
            }
        }
    }
    return false;
}

// Головна рекурсивна функція доведення
bool prove(Sequent seq) {
    // Якщо секвенція тривіально доказова
    if (isAxiom(seq)) return true;

    // Шукаємо складну формулу ЗЛІВА
    for (size_t i = 0; i < seq.left.size(); ++i) {
        auto node = seq.left[i];
        if (node->type == NodeType::VAR) continue;

        // Видаляємо складну формулу з секвенції для застосування правила
        auto newLeft = seq.left;
        newLeft.erase(newLeft.begin() + i);
        
        if (node->type == NodeType::AND) {
            // L-AND: A ∧ B ⊢ ... -> A, B ⊢ ...
            newLeft.push_back(node->left);
            newLeft.push_back(node->right);
            return prove({newLeft, seq.right});
        } 
        else if (node->type == NodeType::OR) {
            // L-OR: A ∨ B ⊢ ... -> A ⊢ ... ТА B ⊢ ... (розгалуження)
            auto leftBranchL = newLeft; leftBranchL.push_back(node->left);
            auto rightBranchL = newLeft; rightBranchL.push_back(node->right);
            return prove({leftBranchL, seq.right}) && prove({rightBranchL, seq.right});
        }
        else if (node->type == NodeType::NOT) {
            // L-NOT: ¬A ⊢ ... -> ⊢ A, ...
            auto newRight = seq.right;
            newRight.push_back(node->left);
            return prove({newLeft, newRight});
        }
    }

    // Шукаємо складну формулу СПРАВА
    for (size_t i = 0; i < seq.right.size(); ++i) {
        auto node = seq.right[i];
        if (node->type == NodeType::VAR) continue;

        auto newRight = seq.right;
        newRight.erase(newRight.begin() + i);

        if (node->type == NodeType::OR) {
            // R-OR: ... ⊢ A ∨ B -> ... ⊢ A, B
            newRight.push_back(node->left);
            newRight.push_back(node->right);
            return prove({seq.left, newRight});
        }
        else if (node->type == NodeType::AND) {
            // R-AND: ... ⊢ A ∧ B -> ... ⊢ A ТА ... ⊢ B (розгалуження)
            auto leftBranchR = newRight; leftBranchR.push_back(node->left);
            auto rightBranchR = newRight; rightBranchR.push_back(node->right);
            return prove({seq.left, leftBranchR}) && prove({seq.left, rightBranchR});
        }
        else if (node->type == NodeType::NOT) {
            // R-NOT: ... ⊢ ¬A -> A, ... ⊢ 
            auto newLeft = seq.left;
            newLeft.push_back(node->left);
            return prove({newLeft, newRight});
        }
    }

    // Немає складних формул і не аксіома -> не доказово
    return false;
}

int main() {
    // Тестуємо Закон виключеного третього: ⊢ A ∨ ¬A
    auto varA = std::make_shared<Node>("A");
    auto notA = std::make_shared<Node>(NodeType::NOT, varA);
    auto lawOfExcludedMiddle = std::make_shared<Node>(NodeType::OR, varA, notA);

    Sequent target;
    target.right.push_back(lawOfExcludedMiddle); // Мета праворуч

    if (prove(target)) {
        std::cout << "Theorem PROVEN!\n";
    } else {
        std::cout << "Theorem INVALID.\n";
    }

    return 0;
}
