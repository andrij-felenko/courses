namespace graph::matching {

enum class ErrorCode {
    Success = 0,
    InvalidParam = -1,
    OutOfMemory = -2,
    IndexOutOfBounds = -3,
    GraphTooLarge = -4,
    StateCorrupted = -5,
    NullPointer = -6
};

enum class Mode {
    Cardinality = 0,
    WeightedExact = 1,
    WeightedApprox = 2
};

struct Allocator {
    std::function<void*(size_t)> custom_malloc;
    std::function<void(void*)> custom_free;
    std::function<void*(void*, size_t)> custom_realloc;
};

} // namespace graph::matching
