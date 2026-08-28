namespace diff {

enum class Algorithm : uint8_t {
    Myers,      // Класичний O(ND) алгоритм Маєрса
    Patience,   // Patience diff (LIS унікальних рядків)
    Histogram,  // Histogram diff (низькочастотні опорні точки)
    Heckel      // Алгоритм Гекеля з підтримкою переміщень блоків
};

enum class Operation : uint8_t {
    Keep,   // Рядок без змін
    Insert, // Додавання
    Delete  // Видалення
};

enum class ErrorCode : int32_t {
    Ok = 0,
    InvalidArgument = -1,
    OutOfMemory = -2,
    LimitExceeded = -3
};

} // namespace diff
