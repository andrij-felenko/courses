namespace feigenbaum {

enum class ErrorCode : int {
    Success = 0,
    InvalidParam = -1,
    MaxItersReached = -2,
    DerivativeZero = -3,
    OutOfMemory = -4,
    NumericalOverflow = -5
};

} // namespace feigenbaum
