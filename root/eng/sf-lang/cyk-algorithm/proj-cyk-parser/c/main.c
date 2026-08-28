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
