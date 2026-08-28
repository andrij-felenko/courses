#include <stdbool.h>

typedef enum {
    NODE_EXPR,
    NODE_STMT,
    NODE_DECL
} NodeKindC;

typedef struct {
    NodeKindC kind;
} ASTNodeC;

typedef struct {
    ASTNodeC base;
    int value;
} ExprNodeC;

bool is_expr_node_c(const ASTNodeC* node) {
    return node && node->kind == NODE_EXPR;
}

ExprNodeC* cast_to_expr_c(ASTNodeC* node) {
    return is_expr_node_c(node) ? (ExprNodeC*)node : 0;
}
