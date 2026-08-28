#include <iostream>
#include <string>
#include <type_traits>

// Категорію ЗАКОДОВАНО у вигляді типу: T& → lvalue, T&& → xvalue, T → prvalue
template <typename T> struct Category      { static constexpr auto name = "prvalue"; };
template <typename T> struct Category<T&>  { static constexpr auto name = "lvalue";  };
template <typename T> struct Category<T&&> { static constexpr auto name = "xvalue";  };

#define VALUE_CATEGORY(expr) (Category<decltype((expr))>::name)

std::string make();            // повертає за значенням
std::string& ref();            // повертає посилання на lvalue
std::string&& expiring();      // повертає посилання на rvalue

int main() {
    std::string s = "текст";
    std::string&& r = make();   // r — ЗМІННА типу «посилання на rvalue»

    std::cout << VALUE_CATEGORY(s)            << '\n';   // lvalue
    std::cout << VALUE_CATEGORY(r)            << '\n';   // lvalue  ← має ім'я!
    std::cout << VALUE_CATEGORY(std::move(s)) << '\n';   // xvalue
    std::cout << VALUE_CATEGORY(make())       << '\n';   // prvalue
    std::cout << VALUE_CATEGORY(ref())        << '\n';   // lvalue
    std::cout << VALUE_CATEGORY(expiring())   << '\n';   // xvalue
    std::cout << VALUE_CATEGORY(s + "!")      << '\n';   // prvalue
    std::cout << VALUE_CATEGORY(s[0])         << '\n';   // lvalue
    std::cout << VALUE_CATEGORY("літерал")    << '\n';   // lvalue
    std::cout << VALUE_CATEGORY(42)           << '\n';   // prvalue
}
