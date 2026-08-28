enum class Status : int32_t {
    Success            =  0,
    ErrNullPointer     = -1,
    ErrOutOfMemory     = -2,
    ErrOracleTimeout   = -3,
    ErrBoundsExceeded  = -4,
    ErrInvalidMachine  = -5
};

enum class OracleType {
    FiniteSet,
    ComputablePredicate,
    HaltingOracle,
    CustomCallback
};
