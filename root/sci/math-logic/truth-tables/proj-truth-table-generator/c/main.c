#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>

typedef enum {
    NODE_VAR,
    NODE_NOT,
    NODE_AND,
    NODE_OR,
    NODE_XOR,
    NODE_IMPLIES
} NodeType;

typedef struct ASTNode {
    NodeType type;
    int var_index;               /* Для NODE_VAR: індекс змінної (0, 1, ...) */
    struct ASTNode* left;        /* Лівий операнд (або єдиний операнд для NOT) */
    struct ASTNode* right;       /* Правий операнд для бінарних операцій */
} ASTNode;

/* Конструктори вузлів AST */
ASTNode* ast_create_var(int var_index) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    if (!node) { perror("malloc failed"); exit(EXIT_FAILURE); }
    node->type = NODE_VAR;
    node->var_index = var_index;
    node->left = NULL;
    node->right = NULL;
    return node;
}

ASTNode* ast_create_unary(NodeType type, ASTNode* child) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    if (!node) { perror("malloc failed"); exit(EXIT_FAILURE); }
    node->type = type;
    node->var_index = -1;
    node->left = child;
    node->right = NULL;
    return node;
}

ASTNode* ast_create_binary(NodeType type, ASTNode* left, ASTNode* right) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    if (!node) { perror("malloc failed"); exit(EXIT_FAILURE); }
    node->type = type;
    node->var_index = -1;
    node->left = left;
    node->right = right;
    return node;
}

/* Рекурсивне звільнення пам'яті */
void ast_free(ASTNode* root) {
    if (!root) return;
    ast_free(root->left);
    ast_free(root->right);
    free(root);
}

/* Оцінка значення AST для заданої бітової маски стану */
bool ast_evaluate(const ASTNode* root, uint32_t state_mask) {
    if (!root) return false;
    
    switch (root->type) {
        case NODE_VAR:
            return (state_mask & (1U << root->var_index)) != 0;
        case NODE_NOT:
            return !ast_evaluate(root->left, state_mask);
        case NODE_AND:
            return ast_evaluate(root->left, state_mask) && ast_evaluate(root->right, state_mask);
        case NODE_OR:
            return ast_evaluate(root->left, state_mask) || ast_evaluate(root->right, state_mask);
        case NODE_XOR:
            return ast_evaluate(root->left, state_mask) ^ ast_evaluate(root->right, state_mask);
        case NODE_IMPLIES: {
            bool left_val = ast_evaluate(root->left, state_mask);
            bool right_val = ast_evaluate(root->right, state_mask);
            return !left_val || right_val; /* P => Q еквівалентно !P || Q */
        }
        default:
            return false;
    }
}

/* Генерація повної таблиці істинності та верифікація */
void print_truth_table(const ASTNode* root, const char* const* var_names, int num_vars) {
    if (num_vars > 31) {
        fprintf(stderr, "Помилка: кількість змінних перевищує 31.\n");
        return;
    }

    /* Друк заголовка таблиці */
    for (int i = 0; i < num_vars; ++i) {
        printf("%s\t", var_names[i]);
    }
    printf("| Результат\n");
    for (int i = 0; i < num_vars * 8 + 12; ++i) putchar('-');
    putchar('\n');

    uint32_t total_rows = 1U << num_vars;
    uint32_t true_count = 0;

    for (uint32_t mask = 0; mask < total_rows; ++mask) {
        for (int i = 0; i < num_vars; ++i) {
            bool bit = (mask & (1U << i)) != 0;
            printf("%d\t", bit ? 1 : 0);
        }
        bool res = ast_evaluate(root, mask);
        if (res) true_count++;
        printf("| %d\n", res ? 1 : 0);
    }

    /* Підсумкова класифікація */
    printf("\nСтатистика: %u/%u істинних наборів.\n", true_count, total_rows);
    if (true_count == total_rows) {
        printf("Висновок: Формула є ТАВТОЛОГІЄЮ (завжди істинна).\n");
    } else if (true_count == 0) {
        printf("Висновок: Формула є СУПЕРЕЧНІСТЮ (тотожна хиба).\n");
    } else {
        printf("Висновок: Формула є ЗДІЙСНЮВАНОЮ (випадкова логічна функція).\n");
    }
}

int main(void) {
    /* Конструюємо формулу Закону Контрапозиції: (P => Q) => (!Q => !P) */
    const char* names[] = {"P", "Q"};
    int num_vars = 2;

    /* Ліва частина: P => Q */
    ASTNode* p1 = ast_create_var(0);
    ASTNode* q1 = ast_create_var(1);
    ASTNode* left_side = ast_create_binary(NODE_IMPLIES, p1, q1);

    /* Права частина: !Q => !P */
    ASTNode* q2 = ast_create_var(1);
    ASTNode* not_q = ast_create_unary(NODE_NOT, q2);
    ASTNode* p2 = ast_create_var(0);
    ASTNode* not_p = ast_create_unary(NODE_NOT, p2);
    ASTNode* right_side = ast_create_binary(NODE_IMPLIES, not_q, not_p);

    /* Повна формула: (P => Q) => (!Q => !P) */
    ASTNode* formula = ast_create_binary(NODE_IMPLIES, left_side, right_side);

    printf("Перевірка виразу: (P => Q) => (!Q => !P)\n\n");
    print_truth_table(formula, names, num_vars);

    ast_free(formula);
    return 0;
}
