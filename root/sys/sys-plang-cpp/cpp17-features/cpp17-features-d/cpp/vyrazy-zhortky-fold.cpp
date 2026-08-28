// 1. Обчислення суми аргументів за допомогою унарної згортки:
template <typename... Args>
auto sum_all(Args... args) {
    return (... + args); // Розгортається компілятором у: (arg1 + (arg2 + ... + argN))
}

// 2. Друк довільної кількості параметрів у потік:
template <typename... Args>
void print_all(const Args&... args) {
    (std::cout << ... << args) << "\n";
}

// 3. Виклик функції валідації для кожного аргументу:
template <typename... Args>
bool validate_all(const Args&... args) {
    return (args.is_valid() && ...); // Логічне І з коротким замиканням
}
