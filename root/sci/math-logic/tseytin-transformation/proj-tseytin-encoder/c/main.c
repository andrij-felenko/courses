#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

/* Типи вузлів синтаксичного дерева */
typedef enum {
    NODE_VAR,
    NODE_NOT,
    NODE_AND,
    NODE_OR,
    NODE_IMPLIES,
    NODE_XOR
} NodeType;

/* Структура вузла AST */
typedef struct ASTNode {
    NodeType type;
    int var_id;                  /* Номер змінної (для NODE_VAR) */
    struct ASTNode* left;
    struct ASTNode* right;
} ASTNode;

/* Динамічний масив диз'юнктів */
typedef struct {
    int* lits;
    size_t size;
    size_t capacity;
} Clause;

typedef struct {
    Clause* data;
    size_t count;
    size_t capacity;
    int max_var;
} TseytinEncoder;

/* Створення вузлів AST */
ASTNode* create_var(int var_id) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = NODE_VAR;
    node->var_id = var_id;
    node->left = NULL;
    node->right = NULL;
    return node;
}

ASTNode* create_unary(NodeType type, ASTNode* child) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var_id = 0;
    node->left = child;
    node->right = NULL;
    return node;
}

ASTNode* create_binary(NodeType type, ASTNode* left, ASTNode* right) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var_id = 0;
    node->left = left;
    node->right = right;
    return node;
}

void free_ast(ASTNode* node) {
    if (!node) return;
    free_ast(node->left);
    free_ast(node->right);
    free(node);
}

/* Управління кодером Цейтіна */
TseytinEncoder* encoder_create(int num_inputs) {
    TseytinEncoder* enc = (TseytinEncoder*)malloc(sizeof(TseytinEncoder));
    enc->count = 0;
    enc->capacity = 16;
    enc->data = (Clause*)malloc(enc->capacity * sizeof(Clause));
    enc->max_var = num_inputs;
    return enc;
}

void encoder_add_clause(TseytinEncoder* enc, const int* lits, size_t size) {
    if (enc->count >= enc->capacity) {
        enc->capacity *= 2;
        enc->data = (Clause*)realloc(enc->data, enc->capacity * sizeof(Clause));
    }
    Clause* c = &enc->data[enc->count++];
    c->size = size;
    c->capacity = size;
    c->lits = (int*)malloc(size * sizeof(int));
    for (size_t i = 0; i < size; ++i) {
        c->lits[i] = lits[i];
    }
}

void encoder_free(TseytinEncoder* enc) {
    if (!enc) return;
    for (size_t i = 0; i < enc->count; ++i) {
        free(enc->data[i].lits);
    }
    free(enc->data);
    free(enc);
}

int encoder_fresh_var(TseytinEncoder* enc) {
    return ++(enc->max_var);
}

/* Рекурсивний обхід AST та генерація КНФ-диз'юнктів */
int tseytin_transform_node(TseytinEncoder* enc, const ASTNode* node) {
    if (!node) return 0;
    if (node->type == NODE_VAR) {
        return node->var_id;
    }

    int left_var = tseytin_transform_node(enc, node->left);
    int right_var = tseytin_transform_node(enc, node->right);
    int out_var = encoder_fresh_var(enc);

    switch (node->type) {
        case NODE_NOT: {
            /* out_var <-> NOT left_var */
            int c1[] = {-out_var, -left_var};
            int c2[] = {out_var, left_var};
            encoder_add_clause(enc, c1, 2);
            encoder_add_clause(enc, c2, 2);
            break;
        }
        case NODE_AND: {
            /* out_var <-> (left_var AND right_var) */
            int c1[] = {-out_var, left_var};
            int c2[] = {-out_var, right_var};
            int c3[] = {out_var, -left_var, -right_var};
            encoder_add_clause(enc, c1, 2);
            encoder_add_clause(enc, c2, 2);
            encoder_add_clause(enc, c3, 3);
            break;
        }
        case NODE_OR: {
            /* out_var <-> (left_var OR right_var) */
            int c1[] = {out_var, -left_var};
            int c2[] = {out_var, -right_var};
            int c3[] = {-out_var, left_var, right_var};
            encoder_add_clause(enc, c1, 2);
            encoder_add_clause(enc, c2, 2);
            encoder_add_clause(enc, c3, 3);
            break;
        }
        case NODE_IMPLIES: {
            /* out_var <-> (left_var -> right_var) */
            int c1[] = {out_var, left_var};
            int c2[] = {out_var, -right_var};
            int c3[] = {-out_var, -left_var, right_var};
            encoder_add_clause(enc, c1, 2);
            encoder_add_clause(enc, c2, 2);
            encoder_add_clause(enc, c3, 3);
            break;
        }
        case NODE_XOR: {
            /* out_var <-> (left_var XOR right_var) */
            int c1[] = {-out_var, -left_var, -right_var};
            int c2[] = {-out_var, left_var, right_var};
            int c3[] = {out_var, -left_var, right_var};
            int c4[] = {out_var, left_var, -right_var};
            encoder_add_clause(enc, c1, 3);
            encoder_add_clause(enc, c2, 3);
            encoder_add_clause(enc, c3, 3);
            encoder_add_clause(enc, c4, 3);
            break;
        }
        default:
            break;
    }
    return out_var;
}

void print_dimacs(const TseytinEncoder* enc, int root_var) {
    /* Кількість клауз = згенеровані + 1 для кореня */
    printf("p cnf %d %zu\n", enc->max_var, enc->count + 1);
    for (size_t i = 0; i < enc->count; ++i) {
        for (size_t j = 0; j < enc->data[i].size; ++j) {
            printf("%d ", enc->data[i].lits[j]);
        }
        printf("0\n");
    }
    printf("%d 0\n", root_var);
}

int main(void) {
    /* Побудова формули F = (A AND B) OR (NOT C) */
    /* Вхідні змінні: 1=A, 2=B, 3=C */
    ASTNode* varA = create_var(1);
    ASTNode* varB = create_var(2);
    ASTNode* varC = create_var(3);

    ASTNode* and_node = create_binary(NODE_AND, varA, varB);
    ASTNode* not_node = create_unary(NODE_NOT, varC);
    ASTNode* root = create_binary(NODE_OR, and_node, not_node);

    TseytinEncoder* enc = encoder_create(3);
    int root_var = tseytin_transform_node(enc, root);

    printf("c Згенерований DIMACS CNF для виразу (A AND B) OR (NOT C)\n");
    print_dimacs(enc, root_var);

    encoder_free(enc);
    free_ast(root);
    return 0;
}
