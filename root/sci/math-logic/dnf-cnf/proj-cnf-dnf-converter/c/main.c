/* 
 * Табличний конвертер булевих форм мовою C (C99)
 * Генерація ДДНФ та ДКНФ за обчисленням значення AST для n змінних.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VARS 10
#define MAX_CLAUSES 1024

typedef enum {
    NODE_VAR,
    NODE_NOT,
    NODE_AND,
    NODE_OR
} NodeType;

typedef struct ASTNode {
    NodeType type;
    char var_name;
    struct ASTNode* left;
    struct ASTNode* right;
} ASTNode;

/* Створення вузла змінної */
ASTNode* create_var(char name) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = NODE_VAR;
    node->var_name = name;
    node->left = NULL;
    node->right = NULL;
    return node;
}

/* Створення унарного/бінарного вузла */
ASTNode* create_op(NodeType type, ASTNode* left, ASTNode* right) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var_name = '\0';
    node->left = left;
    node->right = right;
    return node;
}

/* Звільнення пам'яті AST */
void free_ast(ASTNode* node) {
    if (!node) return;
    free_ast(node->left);
    free_ast(node->right);
    free(node);
}

/* Рекурсивна оцінка AST під задану підстановку змінних */
bool eval_ast(const ASTNode* node, const bool env[26]) {
    if (!node) return false;
    switch (node->type) {
        case NODE_VAR:
            return env[node->var_name - 'A'];
        case NODE_NOT:
            return !eval_ast(node->left, env);
        case NODE_AND:
            return eval_ast(node->left, env) && eval_ast(node->right, env);
        case NODE_OR:
            return eval_ast(node->left, env) || eval_ast(node->right, env);
    }
    return false;
}

/* Друк ДДНФ (Досконала ДНФ) за 1-наборами */
void print_sdnf(const ASTNode* root, const char vars[], int var_count) {
    bool env[26] = {false};
    int total_combinations = 1 << var_count;
    bool first_term = true;

    printf("SDNF: ");
    for (int i = 0; i < total_combinations; ++i) {
        /* Присвоєння значень змінним за бітами числа i */
        for (int j = 0; j < var_count; ++j) {
            env[vars[j] - 'A'] = (i >> (var_count - 1 - j)) & 1;
        }

        if (eval_ast(root, env)) {
            if (!first_term) {
                printf(" ∨ ");
            }
            first_term = false;
            printf("(");
            for (int j = 0; j < var_count; ++j) {
                bool val = env[vars[j] - 'A'];
                if (j > 0) printf(" ∧ ");
                if (!val) {
                    printf("¬%c", vars[j]);
                } else {
                    printf("%c", vars[j]);
                }
            }
            printf(")");
        }
    }
    if (first_term) {
        printf("0 (Тотожна хибність)");
    }
    printf("\n");
}

/* Друк ДКНФ (Досконала КНФ) за 0-наборами */
void print_sknf(const ASTNode* root, const char vars[], int var_count) {
    bool env[26] = {false};
    int total_combinations = 1 << var_count;
    bool first_clause = true;

    printf("SKNF: ");
    for (int i = 0; i < total_combinations; ++i) {
        for (int j = 0; j < var_count; ++j) {
            env[vars[j] - 'A'] = (i >> (var_count - 1 - j)) & 1;
        }

        /* ДКНФ будується за наборами, де формула дорівнює 0 */
        if (!eval_ast(root, env)) {
            if (!first_clause) {
                printf(" ∧ ");
            }
            first_clause = false;
            printf("(");
            for (int j = 0; j < var_count; ++j) {
                bool val = env[vars[j] - 'A'];
                if (j > 0) printf(" ∨ ");
                /* Для 0 береться змінна без заперечення, для 1 - з запереченням */
                if (val) {
                    printf("¬%c", vars[j]);
                } else {
                    printf("%c", vars[j]);
                }
            }
            printf(")");
        }
    }
    if (first_clause) {
        printf("1 (Тотожна істинність)");
    }
    printf("\n");
}

int main(void) {
    /* Побудова формули: (A ∧ B) ∨ ¬C */
    ASTNode* node_a = create_var('A');
    ASTNode* node_b = create_var('B');
    ASTNode* node_ab = create_op(NODE_AND, node_a, node_b);

    ASTNode* node_c = create_var('C');
    ASTNode* node_not_c = create_op(NODE_NOT, node_c, NULL);

    ASTNode* root = create_op(NODE_OR, node_ab, node_not_c);

    char vars[] = {'A', 'B', 'C'};
    int var_count = 3;

    printf("--- Табличний конвертер ДДНФ / ДКНФ (Мова C) ---\n");
    print_sdnf(root, vars, var_count);
    print_sknf(root, vars, var_count);

    free_ast(root);
    return 0;
}
