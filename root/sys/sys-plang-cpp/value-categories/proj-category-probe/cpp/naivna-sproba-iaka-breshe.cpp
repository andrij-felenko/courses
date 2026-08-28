#include <cstdio>
#include <string>
#include <type_traits>
#include <utility>

std::string make();

#define NAIVE(expr) (std::is_reference_v<decltype(expr)> ? "rvalue" : "prvalue")

int main() {
    std::string s = "text";
    std::string&& r = make();

    std::puts(NAIVE(s));             // "prvalue" — а насправді lvalue
    std::puts(NAIVE(r));             // "rvalue"  — а насправді теж lvalue
    std::puts(NAIVE(std::move(s)));  // "rvalue"  — правда, але випадкова
}
