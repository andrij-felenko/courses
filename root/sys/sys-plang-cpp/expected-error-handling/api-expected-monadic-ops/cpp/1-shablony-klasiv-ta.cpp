namespace std {
    // 1. Основний шаблон для результату зі значенням T або помилкою E
    template <typename T, typename E>
    class expected;

    // 2. Спеціалізація для процедур без повернення значення (void)
    template <typename E>
    class expected<void, E>;

    // 3. Явна обгортка для маркування значення помилки
    template <typename E>
    class unexpected;

    // 4. Тип винятку при небезпечному доступі через .value()
    template <typename E>
    class bad_expected_access;
}
