#include <variant>
#include <string>
#include <iostream>

struct CircleShape { double radius; };
struct SquareShape { double side; };
struct TriangleShape { double base, height; };

using ShapeVariant = std::variant<CircleShape, SquareShape, TriangleShape>;

void render_variant(const ShapeVariant& shape) {
    // Безпечний патерн-матчинг без RTTI, vtable та жодних кастів:
    std::visit([](const auto& s) {
        using T = std::decay_t<decltype(s)>;
        if constexpr (std::is_same_v<T, CircleShape>) {
            std::cout << "Коло радіусом " << s.radius << '\n';
        } else if constexpr (std::is_same_v<T, SquareShape>) {
            std::cout << "Квадрат зі стороною " << s.side << '\n';
        } else if constexpr (std::is_same_v<T, TriangleShape>) {
            std::cout << "Трикутник\n";
        }
    }, shape);
}
