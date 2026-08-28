template<typename T>
concept Printable = requires(T a) { std::cout << a; };

template<typename T>
concept FormattedPrintable = Printable<T> && requires(T a) { a.custom_format(); };

// Перевантаження 1: для будь-яких типів із оператором <<
template<Printable T>
void display(T val) {
    std::cout << val << "\n";
}

// Перевантаження 2: для типів із власним методом форматування
template<FormattedPrintable T>
void display(T val) {
    val.custom_format();
}
