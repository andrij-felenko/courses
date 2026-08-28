struct Shape {
    int layer{0};
    auto operator<=>(const Shape&) const = default;
};

struct Circle : Shape {
    double radius{1.0};
    auto operator<=>(const Circle&) const = default;
};

void compare_shapes(const Shape& s1, const Shape& s2) {
    // Небезпечно! Порівнюються ЛИШЕ поля Shape::layer.
    // Поля radius класу Circle повністю ігноруються!
    if ((s1 <=> s2) == 0) {
        // Хибний висновок про еквівалентність різних фігур!
    }
}
