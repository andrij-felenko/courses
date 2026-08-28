namespace horn {

using Var = int32_t;
inline constexpr Var VarNone = -1;

enum class SolutionStatus : uint8_t {
    Sat,
    Unsat
};

enum class ErrorCode : int32_t {
    Ok = 0,
    NullPointer = -1,
    InvalidVar = -2,
    InvalidState = -3,
    OutOfMemory = -4,
    DuplicateLiteral = -5
};

class HornSolver;

} // namespace horn
