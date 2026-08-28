#include <stdbool.h>

typedef enum {
    OP_INSERT,
    OP_DELETE,
    OP_NOOP
} OpType;

typedef struct {
    OpType type;
    int pos;
    char ch;
    int client_id;
} Operation;

/* Попарна трансформація Inclusion Transformation: T(op1, op2) -> (out1, out2) */
void transform_pair(const Operation *op1, const Operation *op2,
                    Operation *out1, Operation *out2) {
    *out1 = *op1;
    *out2 = *op2;

    if (op1->type == OP_NOOP || op2->type == OP_NOOP) {
        return;
    }

    if (op1->type == OP_INSERT && op2->type == OP_INSERT) {
        if (op1->pos < op2->pos || (op1->pos == op2->pos && op1->client_id < op2->client_id)) {
            out2->pos += 1;
        } else {
            out1->pos += 1;
        }
    } else if (op1->type == OP_INSERT && op2->type == OP_DELETE) {
        if (op1->pos <= op2->pos) {
            out2->pos += 1;
        } else {
            out1->pos -= 1;
        }
    } else if (op1->type == OP_DELETE && op2->type == OP_INSERT) {
        if (op1->pos < op2->pos) {
            out2->pos -= 1;
        } else {
            out1->pos += 1;
        }
    } else if (op1->type == OP_DELETE && op2->type == OP_DELETE) {
        if (op1->pos < op2->pos) {
            out2->pos -= 1;
        } else if (op1->pos > op2->pos) {
            out1->pos -= 1;
        } else {
            /* Обидва видалили той самий символ -> перетворюємо на NoOp */
            out1->type = OP_NOOP;
            out2->type = OP_NOOP;
        }
    }
}
