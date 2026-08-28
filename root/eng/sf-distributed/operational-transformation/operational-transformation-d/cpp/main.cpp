#include <utility>
#include <cstdint>

enum class OpType {
    Insert,
    Delete,
    NoOp
};

struct Operation {
    OpType type{OpType::NoOp};
    int pos{0};
    char ch{'\0'};
    int client_id{0};
};

/* Попарна трансформація Inclusion Transformation: T(op1, op2) -> std::pair */
std::pair<Operation, Operation> transform_pair(const Operation &op1, const Operation &op2) {
    Operation out1 = op1;
    Operation out2 = op2;

    if (op1.type == OpType::NoOp || op2.type == OpType::NoOp) {
        return {out1, out2};
    }

    if (op1.type == OpType::Insert && op2.type == OpType::Insert) {
        if (op1.pos < op2.pos || (op1.pos == op2.pos && op1.client_id < op2.client_id)) {
            out2->pos += 1;
        } else {
            out1.pos += 1;
        }
    } else if (op1.type == OpType::Insert && op2.type == OpType::Delete) {
        if (op1.pos <= op2.pos) {
            out2->pos += 1;
        } else {
            out1.pos -= 1;
        }
    } else if (op1.type == OpType::Delete && op2.type == OpType::Insert) {
        if (op1.pos < op2.pos) {
            out2->pos -= 1;
        } else {
            out1.pos += 1;
        }
    } else if (op1.type == OpType::Delete && op2.type == OpType::Delete) {
        if (op1.pos < op2.pos) {
            out2->pos -= 1;
        } else if (op1.pos > op2.pos) {
            out1.pos -= 1;
        } else {
            out1.type = OpType::NoOp;
            out2.type = OpType::NoOp;
        }
    }

    return {out1, out2};
}
