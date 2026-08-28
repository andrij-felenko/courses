/*
 * Об'єктно-орієнтований конвертер булевих форм мовою C++ (C++20)
 * Використання std::unique_ptr, RAII, std::vector та ідіоматичних контейнерів.
 */
#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <unordered_map>
#include <cmath>

enum class OpType { Var, Not, And, Or };

class ASTNode {
public:
    OpType type;
    char var_name{'\0'};
    std::unique_ptr<ASTNode> left;
    std::unique_ptr<ASTNode> right;

    explicit ASTNode(char name) : type(OpType::Var), var_name(name) {}
    ASTNode(OpType op, std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r = nullptr)
        : type(op), left(std::move(l)), right(std::move(r)) {}

    [[nodiscard]] bool evaluate(const std::unordered_map<char, bool>& env) const {
        switch (type) {
            case OpType::Var:
                return env.at(var_name);
            case OpType::Not:
                return !left->evaluate(env);
            case OpType::And:
                return left->evaluate(env) && right->evaluate(env);
            case OpType::Or:
                return left->evaluate(env) || right->evaluate(env);
        }
        return false;
    }
};

class BooleanFormConverter {
private:
    const ASTNode& root_;
    std::vector<char> vars_;

public:
    BooleanFormConverter(const ASTNode& root, std::vector<char> vars)
        : root_(root), vars_(std::move(vars)) {}

    [[nodiscard]] std::string generate_sdnf() const {
        std::string result;
        const size_t num_vars = vars_.size();
        const size_t total_rows = 1ULL << num_vars;
        bool first_term = true;

        for (size_t i = 0; i < total_rows; ++i) {
            std::unordered_map<char, bool> env;
            for (size_t j = 0; j < num_vars; ++j) {
                env[vars_[j]] = ((i >> (num_vars - 1 - j)) & 1ULL) != 0;
            }

            if (root_.evaluate(env)) {
                if (!first_term) {
                    result += " ∨ ";
                }
                first_term = false;
                result += "(";
                for (size_t j = 0; j < num_vars; ++j) {
                    if (j > 0) result += " ∧ ";
                    if (!env[vars_[j]]) {
                        result += "¬";
                    }
                    result += vars_[j];
                }
                result += ")";
            }
        }
        return first_term ? "0" : result;
    }

    [[nodiscard]] std::string generate_sknf() const {
        std::string result;
        const size_t num_vars = vars_.size();
        const size_t total_rows = 1ULL << num_vars;
        bool first_clause = true;

        for (size_t i = 0; i < total_rows; ++i) {
            std::unordered_map<char, bool> env;
            for (size_t j = 0; j < num_vars; ++j) {
                env[vars_[j]] = ((i >> (num_vars - 1 - j)) & 1ULL) != 0;
            }

            if (!root_.evaluate(env)) {
                if (!first_clause) {
                    result += " ∧ ";
                }
                first_clause = false;
                result += "(";
                for (size_t j = 0; j < num_vars; ++j) {
                    if (j > 0) result += " ∨ ";
                    if (env[vars_[j]]) {
                        result += "¬";
                    }
                    result += vars_[j];
                }
                result += ")";
            }
        }
        return first_clause ? "1" : result;
    }
};

int main() {
    // Побудова виразу: (A ∨ B) ∧ (¬A ∨ C)
    auto node_a1 = std::make_unique<ASTNode>('A');
    auto node_b = std::make_unique<ASTNode>('B');
    auto clause1 = std::make_unique<ASTNode>(OpType::Or, std::move(node_a1), std::move(node_b));

    auto node_a2 = std::make_unique<ASTNode>('A');
    auto not_a = std::make_unique<ASTNode>(OpType::Not, std::move(node_a2));
    auto node_c = std::make_unique<ASTNode>('C');
    auto clause2 = std::make_unique<ASTNode>(OpType::Or, std::move(not_a), std::move(node_c));

    auto root = std::make_unique<ASTNode>(OpType::And, std::move(clause1), std::move(clause2));

    std::vector<char> variables = {'A', 'B', 'C'};
    BooleanFormConverter converter(*root, variables);

    std::cout << "--- Конвертер ДДНФ / ДКНФ (Мова C++) ---\n";
    std::cout << "SDNF: " << converter.generate_sdnf() << "\n";
    std::cout << "SKNF: " << converter.generate_sknf() << "\n";

    return 0;
}
