/* C Implementation: FO Model Checker on Finite Graphs */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VARS 16
#define MAX_NODES 1000

typedef struct {
    int num_vertices;
    bool adj[MAX_NODES][MAX_NODES];
} Graph;

typedef enum {
    NODE_PRED_EDGE,   /* E(x, y) */
    NODE_PRED_EQ,     /* x == y */
    NODE_NOT,         /* NOT child */
    NODE_AND,         /* child1 AND child2 */
    NODE_OR,          /* child1 OR child2 */
    NODE_EXISTS,      /* EXISTS var_id child */
    NODE_FORALL       /* FORALL var_id child */
} NodeType;

typedef struct ASTNode {
    NodeType type;
    int var1;
    int var2;
    struct ASTNode *left;
    struct ASTNode *right;
} ASTNode;

/* Створення атомарного предиката E(var1, var2) або (var1 == var2) */
ASTNode* create_pred(NodeType type, int var1, int var2) {
    ASTNode *node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var1 = var1;
    node->var2 = var2;
    node->left = NULL;
    node->right = NULL;
    return node;
}

/* Створення логічного оператора NOT, AND, OR */
ASTNode* create_op(NodeType type, ASTNode *left, ASTNode *right) {
    ASTNode *node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var1 = -1;
    node->var2 = -1;
    node->left = left;
    node->right = right;
    return node;
}

/* Створення квантора EXISTS(var_id, body) або FORALL(var_id, body) */
ASTNode* create_quantifier(NodeType type, int var_id, ASTNode *body) {
    ASTNode *node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->var1 = var_id;
    node->var2 = -1;
    node->left = body;
    node->right = NULL;
    return node;
}

void free_ast(ASTNode *node) {
    if (!node) return;
    free_ast(node->left);
    free_ast(node->right);
    free(node);
}

/* Рекурсивний обчислювач істинності формули щодо середовища env */
bool eval_fo(const ASTNode *node, const Graph *g, int *env) {
    if (!node) return false;

    switch (node->type) {
        case NODE_PRED_EDGE: {
            int u = env[node->var1];
            int v = env[node->var2];
            return g->adj[u][v];
        }
        case NODE_PRED_EQ: {
            return env[node->var1] == env[node->var2];
        }
        case NODE_NOT: {
            return !eval_fo(node->left, g, env);
        }
        case NODE_AND: {
            return eval_fo(node->left, g, env) && eval_fo(node->right, g, env);
        }
        case NODE_OR: {
            return eval_fo(node->left, g, env) || eval_fo(node->right, g, env);
        }
        case NODE_EXISTS: {
            int var_id = node->var1;
            for (int val = 0; val < g->num_vertices; val++) {
                env[var_id] = val;
                if (eval_fo(node->left, g, env)) {
                    return true;
                }
            }
            return false;
        }
        case NODE_FORALL: {
            int var_id = node->var1;
            for (int val = 0; val < g->num_vertices; val++) {
                env[var_id] = val;
                if (!eval_fo(node->left, g, env)) {
                    return false;
                }
            }
            return true;
        }
    }
    return false;
}

int main(void) {
    Graph g;
    g.num_vertices = 4;
    memset(g.adj, 0, sizeof(g.adj));

    /* Створюємо трикутник: 0 -> 1, 1 -> 2, 2 -> 0 */
    g.adj[0][1] = true;
    g.adj[1][2] = true;
    g.adj[2][0] = true;

    /* Формуємо формулу наявності трикутника K3: 
       ∃x ∃y ∃z (E(x,y) ∧ E(y,z) ∧ E(z,x)) */
    ASTNode *e_xy = create_pred(NODE_PRED_EDGE, 0, 1);
    ASTNode *e_yz = create_pred(NODE_PRED_EDGE, 1, 2);
    ASTNode *e_zx = create_pred(NODE_PRED_EDGE, 2, 0);

    ASTNode *conj1 = create_op(NODE_AND, e_xy, e_yz);
    ASTNode *conj2 = create_op(NODE_AND, conj1, e_zx);

    ASTNode *exists_z = create_quantifier(NODE_EXISTS, 2, conj2);
    ASTNode *exists_y = create_quantifier(NODE_EXISTS, 1, exists_z);
    ASTNode *exists_x = create_quantifier(NODE_EXISTS, 0, exists_y);

    int env[MAX_VARS] = {0};
    bool has_triangle = eval_fo(exists_x, &g, env);

    printf("Результат перевірки формули K3: %s\n", has_triangle ? "TRUE" : "FALSE");

    free_ast(exists_x);
    return 0;
}
