# ⚙️ Практична реалізація парсера CYK: розпізнавання, мемоізація та побудова дерева виведення

Ця програмна реалізація демонструє повний цикл роботи алгоритму Кока–Янгера–Касамі (CYK): представлення граматики в нормальній формі Хомського, ініціалізацію та заповнення піраміди динамічного програмування, а також рекурсивне відновлення дерева синтаксичного розбору (Parse Tree / AST) за збереженими зворотними вказівниками (backpointers).

## Архітектурна будова рушія синтаксичного аналізу

Програмний комплекс складається з трьох взаємопов'язаних рівнів абстракції:

1. **Рівень представлення граматики:** Правила граматики суворо розділені на два непересічні масиви — бінарні продукції `A → BC` та термінальні продукції `A → a`. Це розділення дозволяє уникнути поліморфних перевірок у гарячому циклі обчислень та забезпечує максимальну щільність пакування даних у кеш-пам'яті першого рівня (L1 Cache).
2. **Таблиця мемоізації (Chart Table):** Тривимірна піраміда індексується довжиною підрядка `l` (`1 ≤ l ≤ n`) та початковим зміщенням `i` (`1 ≤ i ≤ n - l + 1`). Кожна клітинка містить множину досяжних нетерміналів та однозв'язний список або динамічний масив структур `Backpointer`, які фіксують факт успішного застосування правила для точки розбиття `k`.
3. **Генератор синтаксичного дерева:** Рекурсивний обхідник розгортає таблицю зворотних вказівників від кореневої клітинки `P[n, 1]` вниз до термінального листя, конструюючи строго бінарне дерево абстрактного синтаксису (AST).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_RULES 128
#define MAX_SYMBOLS 64
#define MAX_STR_LEN 64

/* Структура бінарного правила A -> B C */
typedef struct {
    char lhs;
    char rhs1;
    char rhs2;
} BinaryRule;

/* Структура термінального правила A -> a */
typedef struct {
    char lhs;
    char terminal;
} TerminalRule;

/* Граматика в нормальній формі Хомського */
typedef struct {
    char start_symbol;
    BinaryRule binary_rules[MAX_RULES];
    int num_binary;
    TerminalRule terminal_rules[MAX_RULES];
    int num_terminal;
} CNFGrammar;

/* Вузол дерева синтаксичного розбору */
typedef struct ParseTreeNode {
    char symbol;
    char terminal;               /* '\0' якщо це нетермінальний вузол */
    struct ParseTreeNode* left;
    struct ParseTreeNode* right;
} ParseTreeNode;

/* Елемент зворотної історії розбору для побудови дерева */
typedef struct Backpointer {
    char lhs;
    int split_k;
    char rhs1;
    char rhs2;
    struct Backpointer* next;
} Backpointer;

/* Комірка таблиці динамічного програмування */
typedef struct {
    bool has_symbol[256];
    Backpointer* backpointers;
} ChartCell;

/* Створення вузла дерева */
ParseTreeNode* create_tree_node(char symbol, char terminal, ParseTreeNode* left, ParseTreeNode* right) {
    ParseTreeNode* node = (ParseTreeNode*)malloc(sizeof(ParseTreeNode));
    if (!node) return NULL;
    node->symbol = symbol;
    node->terminal = terminal;
    node->left = left;
    node->right = right;
    return node;
}

/* Звільнення пам'яті дерева розбору */
void free_parse_tree(ParseTreeNode* root) {
    if (!root) return;
    free_parse_tree(root->left);
    free_parse_tree(root->right);
    free(root);
}

/* Додавання зворотного вказівника */
void add_backpointer(ChartCell* cell, char lhs, int split_k, char rhs1, char rhs2) {
    Backpointer* bp = (Backpointer*)malloc(sizeof(Backpointer));
    if (!bp) return;
    bp->lhs = lhs;
    bp->split_k = split_k;
    bp->rhs1 = rhs1;
    bp->rhs2 = rhs2;
    bp->next = cell->backpointers;
    cell->backpointers = bp;
}

/* Рекурсивне відновлення дерева синтаксичного розбору */
ParseTreeNode* build_tree(ChartCell*** chart, const char* str, int l, int i, char symbol) {
    ChartCell* cell = &chart[l][i];
    
    /* Базовий випадок: довжина 1 (термінальний листок) */
    if (l == 1) {
        return create_tree_node(symbol, str[i - 1], NULL, NULL);
    }
    
    /* Пошук відповідного правила розбиття */
    Backpointer* bp = cell->backpointers;
    while (bp != NULL) {
        if (bp->lhs == symbol) {
            int k = bp->split_k;
            ParseTreeNode* left = build_tree(chart, str, k, i, bp->rhs1);
            ParseTreeNode* right = build_tree(chart, str, l - k, i + k, bp->rhs2);
            if (left && right) {
                return create_tree_node(symbol, '\0', left, right);
            }
            if (left) free_parse_tree(left);
            if (right) free_parse_tree(right);
        }
        bp = bp->next;
    }
    return NULL;
}

/* Друк синтаксичного дерева з відступами */
void print_tree(const ParseTreeNode* node, int depth) {
    if (!node) return;
    for (int d = 0; d < depth; ++d) printf("  ");
    
    if (node->terminal != '\0') {
        printf("%c -> '%c'\n", node->symbol, node->terminal);
    } else {
        printf("%c\n", node->symbol);
        print_tree(node->left, depth + 1);
        print_tree(node->right, depth + 1);
    }
}

/* Головна функція алгоритму CYK */
bool cyk_parse(const CNFGrammar* grammar, const char* str, ParseTreeNode** out_tree) {
    int n = (int)strlen(str);
    if (n == 0) return false;

    /* Виділення динамічної 2D таблиці розміру (n+1) x (n+1) */
    ChartCell*** chart = (ChartCell***)malloc((n + 1) * sizeof(ChartCell**));
    for (int l = 0; l <= n; ++l) {
        chart[l] = (ChartCell**)malloc((n + 1) * sizeof(ChartCell*));
        for (int i = 0; i <= n; ++i) {
            chart[l][i] = (ChartCell*)calloc(1, sizeof(ChartCell));
        }
    }

    /* 1. Базовий рівень: підрядки довжини l = 1 */
    for (int i = 1; i <= n; ++i) {
        char term = str[i - 1];
        for (int r = 0; r < grammar->num_terminal; ++r) {
            if (grammar->terminal_rules[r].terminal == term) {
                char lhs = grammar->terminal_rules[r].lhs;
                chart[1][i]->has_symbol[(unsigned char)lhs] = true;
            }
        }
    }

    /* 2. Індуктивне заповнення таблиці для довжин l від 2 до n */
    for (int l = 2; l <= n; ++l) {
        for (int i = 1; i <= n - l + 1; ++i) {
            for (int k = 1; k < l; ++k) {
                ChartCell* left_cell = chart[k][i];
                ChartCell* right_cell = chart[l - k][i + k];

                for (int r = 0; r < grammar->num_binary; ++r) {
                    char lhs = grammar->binary_rules[r].lhs;
                    char b = grammar->binary_rules[r].rhs1;
                    char c = grammar->binary_rules[r].rhs2;

                    if (left_cell->has_symbol[(unsigned char)b] &&
                        right_cell->has_symbol[(unsigned char)c]) {
                        chart[l][i]->has_symbol[(unsigned char)lhs] = true;
                        add_backpointer(chart[l][i], lhs, k, b, c);
                    }
                }
            }
        }
    }

    /* 3. Перевірка належності аксіоми S у вершині піраміди P[n, 1] */
    bool accepted = chart[n][1]->has_symbol[(unsigned char)grammar->start_symbol];
    if (accepted && out_tree) {
        *out_tree = build_tree(chart, str, n, 1, grammar->start_symbol);
    } else if (out_tree) {
        *out_tree = NULL;
    }

    /* Звільнення таблиці */
    for (int l = 0; l <= n; ++l) {
        for (int i = 0; i <= n; ++i) {
            Backpointer* bp = chart[l][i]->backpointers;
            while (bp != NULL) {
                Backpointer* tmp = bp;
                bp = bp->next;
                free(tmp);
            }
            free(chart[l][i]);
        }
        free(chart[l]);
    }
    free(chart);

    return accepted;
}

int main(void) {
    /* Приклад граматики у CNF:
       S -> A B | B C
       A -> B A | a
       B -> C C | b
       C -> A B | a
    */
    CNFGrammar g;
    g.start_symbol = 'S';
    g.num_binary = 0;
    g.num_terminal = 0;

    /* Бінарні правила */
    g.binary_rules[g.num_binary++] = (BinaryRule){'S', 'A', 'B'};
    g.binary_rules[g.num_binary++] = (BinaryRule){'S', 'B', 'C'};
    g.binary_rules[g.num_binary++] = (BinaryRule){'A', 'B', 'A'};
    g.binary_rules[g.num_binary++] = (BinaryRule){'B', 'C', 'C'};
    g.binary_rules[g.num_binary++] = (BinaryRule){'C', 'A', 'B'};

    /* Термінальні правила */
    g.terminal_rules[g.num_terminal++] = (TerminalRule){'A', 'a'};
    g.terminal_rules[g.num_terminal++] = (TerminalRule){'B', 'b'};
    g.terminal_rules[g.num_terminal++] = (TerminalRule){'C', 'a'};

    const char* input_str = "baba";
    printf("Синтаксичний аналіз рядка \"%s\" за алгоритмом CYK:\n", input_str);

    ParseTreeNode* tree = NULL;
    bool result = cyk_parse(&g, input_str, &tree);

    if (result) {
        printf("Результат: Слово належить граматиці [ACCEPTED]\n");
        printf("Відновлене дерево виведення:\n");
        print_tree(tree, 0);
        free_parse_tree(tree);
    } else {
        printf("Результат: Слово відхилено [REJECTED]\n");
    }

    return 0;
}
```
```cpp
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
```
:::

## Покроковий аналіз виконання програми

1. **Фаза ініціалізації базового шару:** Для рядка `"baba"` довжини `n = 4` створюються 4 базові клітинки довжини `l = 1`. Перший символ `'b'` активує правило `B → b`, записуючи `{B}` у `chart[1][1]`. Другий символ `'a'` активує правила `A → a` та `C → a`, заповнюючи `chart[1][2]` множиною `{A, C}`.
2. **Фаза індуктивного розбиття:** Для рівня `l = 2` та зміщення `i = 1` (підрядок `"ba"`) єдиною точкою розбиття є `k = 1`. Ліва клітинка `chart[1][1]` містить `{B}`, а права `chart[1][2]` — `{A, C}`. Правило `A → BA` спрацьовує на парі `(B, A)`, а правило `S → BC` — на парі `(B, C)`. Обидва результати записуються в `chart[2][1]` разом зі зворотними вказівниками.
3. **Фаза рекурсивного розгортання дерева:** Після перевірки наявності стартового нетермінала `S` у `chart[4][1]` функція `reconstruct_tree` витягує збережений вказівник `(S, k, B, C)`, створює кореневий вузол та рекурсивно занурюється в ліву клітинку `chart[k][1]` та праву `chart[4-k][1+k]`.

## Ключові відмінності реалізацій на C та C++

1. **Керування часом життя пам'яті (Memory Lifetime):**
   - У версії на C таблиця чарту, зв'язні списки `Backpointer` та вузли синтаксичного дерева виділяються через сирі виклики `malloc`/`calloc`. Для уникнення витоків пам'яті реалізовано дві спеціалізовані функції очищення — поетапне вивільнення вказівників таблиці та рекурсивне звільнення дерева `free_parse_tree`.
   - У версії на C++ застосовано ідіому RAII (Resource Acquisition Is Initialization): дерево представляється через `std::unique_ptr<ParseTreeNode>`, таблиця зберігається в `std::vector<std::vector<ChartCell>>`, а рядки передаються через безпечний невидільний дескриптор `std::string_view`. Усі структури вивільняються автоматично при виході зі спадного контексту навіть у разі виникнення винятків.

2. **Індексація символів та перевірка належності:**
   - C-версія використовує прямий булевий масив `has_symbol[256]` для константного часу перевірки `O(1)`.
   - C++ версія спирається на `std::unordered_set<char>` та метод `contains()` (стандарт C++20), що спрощує читання та зменшує статичний оверхед пам'яті для розріджених клітинок.

3. **Обробка крайових випадків (Edge Cases):**
   - **Порожній рядок (`""`):** Обидва парсери перевіряють нульову довжину на початку та миттєво повертають `false` або `nullptr` без виділення пам'яті таблиці.
   - **Символи поза алфавітом:** Якщо вхідний текст містить літеру, для якої немає термінальних правил `A → a`, відповідна клітинка першого рівня лишається порожньою, і розбір коректно завершується відхиленням без збоїв.

## Обробка неоднозначностей та генерація лісу дерев

У граматиках природних мов одне й те саме речення може породжувати експоненційну кількість синтаксичних дерев. Алгоритм CYK компактно зберігає всі ці дерева у вигляді **спільного упакованого лісу розбору** (Shared Packed Parse Forest, SPPF).

Структура `ChartCell` накопичує всі валідні розбиття `(split_k, rhs1, rhs2)` для одного нетермінала. Замість вибору першого знайденого розбиття, алгоритм може виконати повне комбінаторне розгортання:
- **Генератор усіх дерев:** Рекурсивна функція повертає `std::vector<std::unique_ptr<ParseTreeNode>>`, об'єднуючи всі комбінації лівих і правих піддерев.
- **Ранжування за ймовірністю (Viterbi Best-Tree):** Якщо до правил додано ваги, алгоритм обирає єдине дерево з мінімальною штрафною сумою, не витрачаючи пам'ять на експоненційний перебір варіантів.

## Захист від переповнення системного стека

Для дуже довгих вхідних послідовностей (`n > 1000`), типових для задач біоінформатики або аналізу великих масивів даних, рекурсивне відновлення дерева виведення через глибину викликів `build_tree` може спричинити вичерпання стека потоку (Stack Overflow).

В інженерних реалізаціях рекурсію замінюють ітеративним циклом із явним стеком задач у купі.

## Оптимізації для високонавантажених парсерів

1. **Бітові маски для множин нетерміналів (Bit-parallel parsing):**
   Якщо кількість нетерміналів граматики не перевищує 64 (`|V_N| ≤ 64`), замість хеш-таблиць або булевих масивів кожна клітинка `ChartCell` представляється єдиним 64-бітним цілим числом `uint64_t mask`. Перевірка наявності пари `(B, C)` зводиться до швидких побітових операцій процесора:

:::tabs
```c
uint64_t b_mask = chart[k][i].mask;
uint64_t c_mask = chart[l - k][i + k].mask;
if ((b_mask & (1ULL << rule.rhs1)) && (c_mask & (1ULL << rule.rhs2))) {
    chart[l][i].mask |= (1ULL << rule.lhs);
}
```
```cpp
uint64_t b_mask = chart[k][i].mask;
uint64_t c_mask = chart[l - k][i + k].mask;
if ((b_mask & (1ULL << rule.rhs1)) && (c_mask & (1ULL << rule.rhs2))) {
    chart[l][i].mask |= (1ULL << rule.lhs);
}
```
:::

2. **Зворотне індексування пар `(B, C) → { A }`:**
   Замість лінійного перебору всіх бінарних правил граматики на кожній ітерації внутрішнього циклу, попередньо будується двовимірна матриця зворотного індексу `lookup[B][C] = list(A)`. Завдяки цьому внутрішній цикл ітерується лише за парами нетерміналів, які реально присутні в лівій та правій підклітинах таблиці.

3. **Локальність даних у кеші (Cache Locality):**
   Використання тривимірного одновимірного вектора `chart[l * n + i]` із послідовним розташуванням клітинок у неперервному блоці пам'яті усуває затримки випадкового доступу та запобігає фрагментації оперативної пам'яті.
