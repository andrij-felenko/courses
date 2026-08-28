#include <iostream>
#include <typeinfo>
#include <vector>
#include <string>

#if defined(__GNUC__) || defined(__clang__)
#include <cxxabi.h>
#include <memory>

std::string demangled_typename(const std::type_info& ti) {
    int status = 0;
    std::unique_ptr<char, void(*)(void*)> res{
        abi::__cxa_demangle(ti.name(), nullptr, nullptr, &status),
        std::free
    };
    return (status == 0 && res) ? std::string(res.get()) : ti.name();
}
#else
std::string demangled_typename(const std::type_info& ti) {
    // На MSVC typeid().name() вже містить декодований людиночитабельний рядок
    return ti.name();
}
#endif

int main() {
    std::vector<int> numbers;
    std::cout << "Сире ім'я typeid:   " << typeid(numbers).name() << '\n';
    std::cout << "Людиночитабельне:  " << demangled_typename(typeid(numbers)) << '\n';
}
