#if defined(__GNUC__) || defined(__clang__)
typedef struct __attribute__((aligned(64))) {
    uint64_t count;
    double mean;
    double M2;
    double M3;
    double M4;
    double min_val;
    double max_val;
} welford_aligned_acc_t;
#elif defined(_MSC_VER)
typedef __declspec(align(64)) struct {
    uint64_t count;
    double mean;
    double M2;
    double M3;
    double M4;
    double min_val;
    double max_val;
} welford_aligned_acc_t;
#endif
