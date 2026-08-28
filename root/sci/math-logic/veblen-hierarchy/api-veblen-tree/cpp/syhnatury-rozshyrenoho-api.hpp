namespace veblen {
    /* Генерація n-го члена фундаментальної послідовності для граничного ординала lambda */
    OrdinalPtr fundamental_sequence(const Ordinal* lambda, unsigned long long n);

    /* Предикати типу ординалу */
    [[nodiscard]] bool is_limit(const Ordinal* n) noexcept;
    [[nodiscard]] bool is_successor(const Ordinal* n) noexcept;

    /* Обчислення трансфінітної різниці a - b (якщо a >= b) */
    OrdinalPtr subtract(const Ordinal* a, const Ordinal* b);
}
