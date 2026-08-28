// 1. Первинний шаблон із фіктивним параметром Enable = void
template<typename T, typename Enable = void>
struct Formatter {
    static void format(const T& val) {
        std::cout << "Базове загальне форматування об'єкта\n";
    }
};

// 2. Спеціалізація для цілих типів
template<typename T>
struct Formatter<T, std::enable_if_t<std::is_integral_v<T>>> {
    static void format(const T& val) {
        std::cout << "Швидке форматування цілого числа: " << val << "\n";
    }
};

// 3. Спеціалізація для покажчиків
template<typename T>
struct Formatter<T, std::enable_if_t<std::is_pointer_v<T>>> {
    static void format(const T& val) {
        std::cout << "Шістнадцятковий вивід адреси: " << static_cast<const void*>(val) << "\n";
    }
};
