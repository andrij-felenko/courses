#include <cstdint>

enum class CCOperation : uint32_t {
    None = 0,
    Add,
    Sub,
    Logic,
    Shr
};

bool compute_flag_z(const CPUState& env) noexcept {
    return env.cc_dst == 0;
}

bool compute_flag_s(const CPUState& env) noexcept {
    return static_cast<int32_t>(env.cc_dst) < 0;
}

bool compute_flag_c(const CPUState& env) noexcept {
    switch (static_cast<CCOperation>(env.cc_op)) {
        case CCOperation::Add:
            return env.cc_dst < env.cc_src1;
        case CCOperation::Sub:
            return env.cc_src1 < env.cc_src2;
        case CCOperation::Shr:
            if (env.cc_src2 == 0) return false;
            return (env.cc_src1 >> (env.cc_src2 - 1)) & 1;
        case CCOperation::Logic:
            return false;
        default:
            return false;
    }
}

bool compute_flag_o(const CPUState& env) noexcept {
    switch (static_cast<CCOperation>(env.cc_op)) {
        case CCOperation::Add:
            return (((env.cc_src1 ^ ~env.cc_src2) & (env.cc_src1 ^ env.cc_dst)) >> 31) & 1;
        case CCOperation::Sub:
            return (((env.cc_src1 ^ env.cc_src2) & (env.cc_src1 ^ env.cc_dst)) >> 31) & 1;
        case CCOperation::Logic:
            return false;
        default:
            return false;
    }
}

bool compute_flag_p(const CPUState& env) noexcept {
    uint8_t byte = static_cast<uint8_t>(env.cc_dst & 0xFF);
    byte ^= byte >> 4;
    byte ^= byte >> 2;
    byte ^= byte >> 1;
    return (byte & 1) == 0; // 1 якщо кількість бітів парна
}
