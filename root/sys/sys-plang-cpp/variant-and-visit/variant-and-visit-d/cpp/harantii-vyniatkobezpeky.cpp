#include <variant>
#include <iostream>
#include <string>

struct ThrowingCopy {
    int id;
    ThrowingCopy(int i) : id(i) {}
    
    ThrowingCopy(const ThrowingCopy&) {
        throw std::runtime_error("Помилка під час копіювання!");
    }
    
    ThrowingCopy& operator=(const ThrowingCopy&) = default;
};

int main() {
    std::variant<int, ThrowingCopy> v = 42;
    
    ThrowingCopy bad_obj(100);
    try {
        // Присвоєння викликає знищення int, а потім копіювання ThrowingCopy, яке кидає виняток
        v = bad_obj;
    } catch (const std::exception& e) {
        std::cout << "Впіймали виняток: " << e.what() << "\n";
    }
    
    if (v.valueless_by_exception()) {
        std::cout << "Варіант перейшов у стан valueless_by_exception (index = variant_npos)\n";
    }
    
    // Відновлення валідності варіанта через emplace
    v.emplace<int>(100);
    std::cout << "Після emplace v.index() = " << v.index() << "\n";
}
