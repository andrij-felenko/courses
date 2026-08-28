#include <iostream>

// Допоміжна функція для одинарного значення
template <typename T>
void print_element(const T& val) {
    std::cout << val << " ";
}

template <typename... Args>
void print_all(const Args&... args) {
    // У C++17 вираз згортки для некваліфікованого виклику print_element:
    (print_element(args), ...); 
}

namespace custom {
    struct MyData {
        int id;
    };

    // Перевантаження для MyData оголошене ПІСЛЯ шаблону print_all!
    void print_element(const MyData& d) {
        std::cout << "[MyData:" << d.id << "] ";
    }
}

int main() {
    custom::MyData d1{10}, d2{20};
    print_all(d1, d2); // Викличе custom::print_element через ADL на Фазі 2!
}
