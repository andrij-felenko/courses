// adl-lab.cpp — лабораторія пошуку імен. C++20, жодних залежностей.
#include <concepts>
#include <iostream>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

void head(std::string_view t) { std::cout << "\n──  " << t << "  ──\n"; }
void ask (std::string_view t) { std::cout << "    " << t << "  →  "; }
void say (std::string_view t) { std::cout << t << '\n'; }

namespace lib {                       // чужа бібліотека, яку ми не редагуємо

struct Widget { int id = 0; };
struct Point  { int x = 0, y = 0; };

struct Pixel {
    int x = 0, y = 0;
    friend std::ostream& operator<<(std::ostream& os, const Pixel& p) {   // прихований друг
        return os << '[' << p.x << ", " << p.y << ']';
    }
};

// «зручність», покладена у ЗОВНІШНІЙ простір бібліотеки
template <class T>
void trace(T&& v) {
    (void)v;
    std::cout << "lib::trace<T&&> (загальний шаблон), T&& звівся до "
              << (std::is_const_v<std::remove_reference_t<T>> ? "const&" : "&") << '\n';
}

void onlyAdl(const Widget&) { say("lib::onlyAdl — інакше її не дістати"); }

}  // namespace lib

namespace app {                       // наш код

std::ostream& operator<<(std::ostream& os, const lib::Point& p) {   // ← оператор не в тому просторі
    return os << '(' << p.x << ", " << p.y << ')';
}

void trace(const lib::Widget&) { say("app::trace(const Widget&) — наш, спеціальний"); }

}  // namespace app

namespace util {                      // третій простір: узагальнений друкар
template <class T>
void dump(std::string_view label, const T& v) {
    std::cout << "    " << label << "  →  " << v << '\n';
}
}
