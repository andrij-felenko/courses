#include <any>

std::any a = 42;
a = std::string("dynamically typed payload");

if (a.has_value()) {
    const std::type_info& ti = a.type(); // Інформація RTTI
    if (ti == typeid(std::string)) {
        std::string val = std::any_cast<std::string>(a);
    }
}

// Отримання через покажчик без винятків:
if (std::string* ptr = std::any_cast<std::string>(&a)) {
    std::cout << *ptr << "\n";
}
