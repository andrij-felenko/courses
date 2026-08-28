template <typename... Args>
auto sum_all(Args... args) {
    return (args + ...); // Унарна права згортка: a1 + (a2 + (a3 + a4))
}

template <typename... Args>
void print_spaced(const Args&... args) {
    // Бінарна ліва згортка для потоку введення-виведення
    (std::cout << ... << args) << '\n';
}
