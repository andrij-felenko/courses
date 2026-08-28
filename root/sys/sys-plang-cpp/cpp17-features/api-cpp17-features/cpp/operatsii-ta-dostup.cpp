#include <variant>

std::variant<int, double, std::string> v = "system"s;

// 1. Перевірка активного типу
bool is_str = std::holds_alternative<std::string>(v);
std::size_t active_idx = v.index(); // Повертає 2

// 2. Отримання значення за типом або індексом
std::string& s = std::get<std::string>(v); // Кидає std::bad_variant_access при невідповідності
std::string& s2 = std::get<2>(v);

// 3. Безпечне отримання через вказівник
if (double* p = std::get_if<double>(&v)) {
    // Вказівник не nullptr, якщо активним є double
}

// 4. Патерн відвідувача через ідіому Overloaded
template <class... Ts>
struct overloaded : Ts... { using Ts::operator()...; };
template <class... Ts>
overloaded(Ts...) -> overloaded<Ts...>;

std::visit(overloaded {
    [](int arg) { std::cout << "int: " << arg << "\n"; },
    [](double arg) { std::cout << "double: " << arg << "\n"; },
    [](const std::string& arg) { std::cout << "string: " << arg << "\n"; }
}, v);
