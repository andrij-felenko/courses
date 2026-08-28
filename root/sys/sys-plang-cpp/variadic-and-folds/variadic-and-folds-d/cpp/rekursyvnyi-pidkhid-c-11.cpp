// 1. Базовий випадок (термінатор рекурсії для 0 аргументів)
void print_all() {
    std::cout << '\n';
}

// 2. Рекурсивний шаблон
template <typename Head, typename... Tail>
void print_all(const Head& head, const Tail&... tail) {
    std::cout << head << ' ';
    print_all(tail...); // Рекурсивний виклик для залишку пакета
}
