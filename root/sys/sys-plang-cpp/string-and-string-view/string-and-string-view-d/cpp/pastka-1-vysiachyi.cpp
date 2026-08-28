std::string get_filename() {
    return "data_2026.log";
}

// КАТАСТРОФА: get_filename() повертає тимчасовий std::string.
// Після завершення ініціалізації sv тимчасовий рядок знищується!
std::string_view sv = get_filename(); 

// Помилка під час виконання: читання звільненої пам'яті (Use-After-Free)
std::cout << sv; // UB!
