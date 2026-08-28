#pragma once
#include <cstdint>
#include <system_error>

namespace jinv {

enum class ErrorCode {
    Ok = 0,
    SingularCurve,
    DivisionByZero,
    InvalidParam,
    NoRoot,
    BufferOverflow
};

struct FieldElement2 {
    int64_t re{0};
    int64_t im{0};
};

struct GeneralWeierstrassCurve {
    FieldElement2 a1, a2, a3, a4, a6;
};

struct ShortWeierstrassCurve {
    FieldElement2 a;
    FieldElement2 b;
};

} // namespace jinv
