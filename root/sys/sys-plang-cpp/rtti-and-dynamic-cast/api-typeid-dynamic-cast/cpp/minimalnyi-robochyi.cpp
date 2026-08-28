#include <typeinfo>
#include <typeindex>
#include <unordered_map>
#include <functional>
#include <memory>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cxxabi.h>

struct Shape   { virtual ~Shape() = default; };
struct Circle  : Shape { double r = 2.5; };
struct Polygon : Shape { int n = 5; };
struct Regular : Polygon {};

std::string human(const std::type_info& t) {
    int status = 0;
    char* raw = abi::__cxa_demangle(t.name(), nullptr, nullptr, &status);
    std::string out = (status == 0 && raw) ? raw : t.name();
    std::free(raw);
    return out;
}

int main() {
    using Dump = std::function<void(const Shape&)>;
    std::unordered_map<std::type_index, Dump> registry;

    // ключ — точний тип, тому в обробнику static_cast уже безпечний
    registry[typeid(Circle)]  = [](const Shape& s) {
        std::printf("коло r=%g\n", static_cast<const Circle&>(s).r); };
    registry[typeid(Polygon)] = [](const Shape& s) {
        std::printf("многокутник n=%d\n", static_cast<const Polygon&>(s).n); };

    std::unique_ptr<Shape> s = std::make_unique<Regular>();

    std::printf("динамічний тип:  %s\n", human(typeid(*s)).c_str());   // Regular
    std::printf("тип виразу `s`:  %s\n", human(typeid(s)).c_str());    // unique_ptr<Shape,…>

    auto it = registry.find(typeid(*s));
    std::printf("у реєстрі: %s\n", it == registry.end() ? "не знайдено" : "знайдено");

    if (auto* p = dynamic_cast<Polygon*>(s.get()))   // спрацює: Regular — різновид Polygon
        std::printf("сторін: %d\n", p->n);

    try { (void)dynamic_cast<Circle&>(*s); }
    catch (const std::bad_cast& e) { std::printf("bad_cast: %s\n", e.what()); }
}
