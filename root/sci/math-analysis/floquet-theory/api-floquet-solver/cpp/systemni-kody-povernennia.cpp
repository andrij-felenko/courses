enum class FloquetStatus : int32_t {
    Success             =  0,
    InvalidParam        = -1,
    IntegrationFailure  = -2,
    EigenvalueFailure   = -3,
    AllocationError     = -4
};

struct FloquetConfig {
    std::size_t dim{2};
    double period{3.14159265358979323846};
    std::size_t steps{1000};
    double tolerance{1e-5};
};
