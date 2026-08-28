struct PolygonShape {
    std::array<Vec2, 4> vertices{};
    size_t count{4};
};

struct CircleShape {
    Vec2 center{0.0f, 0.0f};
    float radius{1.0f};
};

int main() {
    PolygonShape box1{
        .vertices = { Vec2{0, 0}, Vec2{2, 0}, Vec2{2, 2}, Vec2{0, 2} },
        .count = 4
    };
    PolygonShape box2{
        .vertices = { Vec2{1, 1}, Vec2{3, 1}, Vec2{3, 3}, Vec2{1, 3} },
        .count = 4
    };

    auto poly_sup = [](const PolygonShape& p, Vec2 d) {
        return polygon_support(std::span<const Vec2>(p.vertices.data(), p.count), d);
    };
    auto circle_sup = [](const CircleShape& c, Vec2 d) {
        return circle_support(c.center, c.radius, d);
    };

    bool hit1 = gjk_intersect_2d(box1, poly_sup, box2, poly_sup);
    std::cout << "Тест 1 (Перетин прямокутників): " << (hit1 ? "ПЕРЕТИН (ОК)" : "ПОМИЛКА") << "\n";

    CircleShape circle{ .center = {1.0f, 1.0f}, .radius = 0.5f };
    bool hit2 = gjk_intersect_2d(box1, poly_sup, circle, circle_sup);
    std::cout << "Тест 2 (Коло в прямокутнику): " << (hit2 ? "ПЕРЕТИН (ОК)" : "ПОМИЛКА") << "\n";

    PolygonShape box3{
        .vertices = { Vec2{5, 5}, Vec2{7, 5}, Vec2{7, 7}, Vec2{5, 7} },
        .count = 4
    };
    bool hit3 = gjk_intersect_2d(box1, poly_sup, box3, poly_sup);
    std::cout << "Тест 3 (Розділені прямокутники): " << (!hit3 ? "РОЗДІЛЕНІ (ОК)" : "ПОМИЛКА") << "\n";

    return 0;
}
