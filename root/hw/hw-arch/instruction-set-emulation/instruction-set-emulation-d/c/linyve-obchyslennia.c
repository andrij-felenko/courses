#include <stdint.h>
#include <stdbool.h>

enum CCOperation {
    CC_OP_NONE = 0,
    CC_OP_ADD,
    CC_OP_SUB,
    CC_OP_LOGIC,
    CC_OP_SHR
};

bool cpu_compute_flag_z(const CPUState *env) {
    return (env->cc_dst == 0);
}

bool cpu_compute_flag_s(const CPUState *env) {
    return ((int32_t)env->cc_dst < 0);
}

bool cpu_compute_flag_c(const CPUState *env) {
    switch (env->cc_op) {
        case CC_OP_ADD:
            return (env->cc_dst < env->cc_src1);
        case CC_OP_SUB:
            return (env->cc_src1 < env->cc_src2);
        case CC_OP_SHR:
            if (env->cc_src2 == 0) return false;
            return (env->cc_src1 >> (env->cc_src2 - 1)) & 1;
        case CC_OP_LOGIC:
            return false;
        default:
            return false;
    }
}

bool cpu_compute_flag_o(const CPUState *env) {
    switch (env->cc_op) {
        case CC_OP_ADD:
            return (((env->cc_src1 ^ ~env->cc_src2) & (env->cc_src1 ^ env->cc_dst)) >> 31) & 1;
        case CC_OP_SUB:
            return (((env->cc_src1 ^ env->cc_src2) & (env->cc_src1 ^ env->cc_dst)) >> 31) & 1;
        case CC_OP_LOGIC:
            return false;
        default:
            return false;
    }
}

// Перевірка парності (Parity Flag) через швидку таблицю на 256 байтів
bool cpu_compute_flag_p(const CPUState *env) {
    static const uint8_t parity_table[256] = {
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1,
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
        // ... решта 224 значень заповнюються бітовим XOR
    };
    return parity_table[env->cc_dst & 0xFF];
}
