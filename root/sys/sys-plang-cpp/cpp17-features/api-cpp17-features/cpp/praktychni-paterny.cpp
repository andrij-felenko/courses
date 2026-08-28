// 1. Логічна перевірка валідності всіх аргументів
template <typename... Args>
bool all_positive(Args... args) {
    return (... && (args > 0)); // Унарна ліва згортка через оператор &&
}

// 2. Потоковий друк елементів
template <typename... Args>
void print_lines(const Args&... args) {
    ((std::cout << args << '\n'), ...); // Унарна права згортка через кому
}

// 3. Додавання елементів у вектор
template <typename T, typename... Args>
void push_many(std::vector<T>& vec, Args&&... args) {
    (vec.push_back(std::forward<Args>(args)), ...);
}
