#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <unordered_set>
#include <unordered_map>
#include <optional>

/* Структура бінарного правила A -> B C */
struct BinaryRule {
    char lhs;
    char rhs1;
    char rhs2;
};

/* Структура термінального правила A -> a */
struct TerminalRule {
    char lhs;
    char terminal;
};

/* Вузол дерева синтаксичного розбору (RAII) */
struct ParseTreeNode {
    char symbol;
    std::optional<char> terminal;
    std::unique_ptr<ParseTreeNode> left;
    std::unique_ptr<ParseTreeNode> right;

    ParseTreeNode(char sym, char term)
        : symbol(sym), terminal(term), left(nullptr), right(nullptr) {}

    ParseTreeNode(char sym, std::unique_ptr<ParseTreeNode> l, std::unique_ptr<ParseTreeNode> r)
        : symbol(sym), terminal(std::nullopt), left(std::move(l)), right(std::move(r)) {}
};

/* Зворотний вказівник для відновлення синтаксичного дерева */
struct Backpointer {
    char lhs;
    size_t split_k;
    char rhs1;
    char rhs2;
};

/* Комірка таблиці динамічного програмування */
struct ChartCell {
    std::unordered_set<char> symbols;
    std::vector<Backpointer> backpointers;
};

/* Клас парсера CYK для граматик у нормальній формі Хомського */
class CYKParser {
public:
    explicit CYKParser(char start_sym) : start_symbol_(start_sym) {}

    void add_binary_rule(char lhs, char rhs1, char rhs2) {
        binary_rules_.push_back({lhs, rhs1, rhs2});
    }

    void add_terminal_rule(char lhs, char terminal) {
        terminal_rules_.push_back({lhs, terminal});
    }

    /* Розпізнавання та відновлення дерева розбору */
    std::pair<bool, std::unique_ptr<ParseTreeNode>> parse(std::string_view input) const {
        const size_t n = input.length();
        if (n == 0) return {false, nullptr};

        /* Таблиця chart[l][i], де l = 1..n (довжина), i = 1..n (початок) */
        std::vector<std::vector<ChartCell>> chart(n + 1, std::vector<ChartCell>(n + 1));

        /* 1. Базовий рівень (довжина l = 1) */
        for (size_t i = 1; i <= n; ++i) {
            char term = input[i - 1];
            for (const auto& rule : terminal_rules_) {
                if (rule.terminal == term) {
                    chart[1][i].symbols.insert(rule.lhs);
                }
            }
        }

        /* 2. Заповнення піраміди підрядків для l = 2..n */
        for (size_t l = 2; l <= n; ++l) {
            for (size_t i = 1; i <= n - l + 1; ++i) {
                for (size_t k = 1; k < l; ++k) {
                    const auto& left_cell = chart[k][i];
                    const auto& right_cell = chart[l - k][i + k];

                    for (const auto& rule : binary_rules_) {
                        if (left_cell.symbols.contains(rule.rhs1) &&
                            right_cell.symbols.contains(rule.rhs2)) {
                            chart[l][i].symbols.insert(rule.lhs);
                            chart[l][i].backpointers.push_back({rule.lhs, k, rule.rhs1, rule.rhs2});
                        }
                    }
                }
            }
        }

        /* 3. Перевірка наявності аксіоми у верхівці chart[n][1] */
        bool accepted = chart[n][1].symbols.contains(start_symbol_);
        std::unique_ptr<ParseTreeNode> tree = nullptr;

        if (accepted) {
            tree = reconstruct_tree(chart, input, n, 1, start_symbol_);
        }

        return {accepted, std::move(tree)};
    }

    /* Друк дерева виведення в консоль */
    static void print_tree(const ParseTreeNode* node, size_t depth = 0) {
        if (!node) return;
        std::string indent(depth * 2, ' ');
        if (node->terminal.has_value()) {
            std::cout << indent << node->symbol << " -> '" << *node->terminal << "'\n";
        } else {
            std::cout << indent << node->symbol << "\n";
            print_tree(node->left.get(), depth + 1);
            print_tree(node->right.get(), depth + 1);
        }
    }

private:
    char start_symbol_;
    std::vector<BinaryRule> binary_rules_;
    std::vector<TerminalRule> terminal_rules_;

    /* Рекурсивне відновлення дерева за зворотними вказівниками */
    std::unique_ptr<ParseTreeNode> reconstruct_tree(
        const std::vector<std::vector<ChartCell>>& chart,
        std::string_view input,
        size_t l,
        size_t i,
        char symbol) const {

        if (l == 1) {
            return std::make_unique<ParseTreeNode>(symbol, input[i - 1]);
        }

        for (const auto& bp : chart[l][i].backpointers) {
            if (bp.lhs == symbol) {
                auto left = reconstruct_tree(chart, input, bp.split_k, i, bp.rhs1);
                auto right = reconstruct_tree(chart, input, l - bp.split_k, i + bp.split_k, bp.rhs2);
                if (left && right) {
                    return std::make_unique<ParseTreeNode>(symbol, std::move(left), std::move(right));
                }
            }
        }
        return nullptr;
    }
};

int main() {
    /* Ініціалізація граматики у CNF */
    CYKParser parser('S');

    /* Додавання бінарних правил */
    parser.add_binary_rule('S', 'A', 'B');
    parser.add_binary_rule('S', 'B', 'C');
    parser.add_binary_rule('A', 'B', 'A');
    parser.add_binary_rule('B', 'C', 'C');
    parser.add_binary_rule('C', 'A', 'B');

    /* Додавання термінальних правил */
    parser.add_terminal_rule('A', 'a');
    parser.add_terminal_rule('B', 'b');
    parser.add_terminal_rule('C', 'a');

    std::string_view input = "baba";
    std::cout << "Синтаксичний аналіз рядка \"" << input << "\" за алгоритмом CYK:\n";

    auto [accepted, tree] = parser.parse(input);

    if (accepted) {
        std::cout << "Результат: Слово належить граматиці [ACCEPTED]\n";
        std::cout << "Відновлене дерево виведення:\n";
        CYKParser::print_tree(tree.get());
    } else {
        std::cout << "Результат: Слово відхилено [REJECTED]\n";
    }

    return 0;
}
