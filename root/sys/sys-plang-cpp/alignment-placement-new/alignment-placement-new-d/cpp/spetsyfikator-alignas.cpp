// 1. Змінна на стеку буде вирівняна по межі 64 байтів (початок кеш-лінії)
alignas(64) int aligned_counter = 0;

// 2. Буфер, вирівняний під суворі вимоги типу double
alignas(double) std::byte storage[sizeof(double)];

// 3. Структура, вирівняна для швидких векторних інструкцій AVX-512
struct alignas(64) AVXBlock {
    float values[16];
};
