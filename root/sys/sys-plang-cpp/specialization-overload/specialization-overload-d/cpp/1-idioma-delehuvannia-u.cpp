namespace detail {

// Первинний шаблон допоміжної структури
template<typename T>
struct FormatterHelper {
    static void print(const T& val) {
        std::cout << "General value: " << val << "\n";
    }
};

// Часткова спеціалізація для вказівників T*
template<typename T>
struct FormatterHelper<T*> {
    static void print(const T* ptr) {
        if (ptr) {
            std::cout << "Pointer to: ";
            FormatterHelper<T>::print(*ptr); // Рекурсивне делегування
        } else {
            std::cout << "Null pointer\n";
        }
    }
};

// Повна спеціалізація для const char*
template<>
struct FormatterHelper<const char*> {
    static void print(const char* str) {
        std::cout << "C-String: \"" << (str ? str : "") << "\"\n";
    }
};

} // namespace detail

// ЄДИНА публічна функція інтерфейсу
template<typename T>
void format_and_print(const T& value) {
    detail::FormatterHelper<T>::print(value);
}
