struct AllocatorTag {};
struct ComparatorTag {};
struct LoggerPolicy {};

struct MultiOptimized : private AllocatorTag,
                        private ComparatorTag,
                        private LoggerPolicy {
    int* data;
};

static_assert(sizeof(MultiOptimized) == sizeof(int*)); // Рівно 8 байтів!
