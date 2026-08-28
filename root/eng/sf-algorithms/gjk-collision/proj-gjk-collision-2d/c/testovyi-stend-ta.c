typedef struct {
    Vec2 vertices[4];
    int count;
} PolygonShape;

typedef struct {
    Vec2 center;
    float radius;
} CircleShape;

static Vec2 poly_support_adapter(const void* shape, Vec2 dir) {
    const PolygonShape* poly = (const PolygonShape*)shape;
    return polygon_support(poly->vertices, poly->count, dir);
}

static Vec2 circle_support_adapter(const void* shape, Vec2 dir) {
    const CircleShape* circle = (const CircleShape*)shape;
    return circle_support(circle->center, circle->radius, dir);
}

int main(void) {
    /* Тест 1: Перетин двох прямокутників */
    PolygonShape box1 = {
        .vertices = { {0, 0}, {2, 0}, {2, 2}, {0, 2} },
        .count = 4
    };
    PolygonShape box2 = {
        .vertices = { {1, 1}, {3, 1}, {3, 3}, {1, 3} },
        .count = 4
    };
    bool hit1 = gjk_intersect_2d(&box1, poly_support_adapter, &box2, poly_support_adapter);
    printf("Тест 1 (Перетин прямокутників): %s\n", hit1 ? "ПЕРЕТИН (ОК)" : "ПОМИЛКА");

    /* Тест 2: Коло всередині прямокутника */
    CircleShape circle = { .center = { 1.0f, 1.0f }, .radius = 0.5f };
    bool hit2 = gjk_intersect_2d(&box1, poly_support_adapter, &circle, circle_support_adapter);
    printf("Тест 2 (Коло в прямокутнику): %s\n", hit2 ? "ПЕРЕТИН (ОК)" : "ПОМИЛКА");

    /* Тест 3: Розділені прямокутники */
    PolygonShape box3 = {
        .vertices = { {5, 5}, {7, 5}, {7, 7}, {5, 7} },
        .count = 4
    };
    bool hit3 = gjk_intersect_2d(&box1, poly_support_adapter, &box3, poly_support_adapter);
    printf("Тест 3 (Розділені прямокутники): %s\n", !hit3 ? "РОЗДІЛЕНІ (ОК)" : "ПОМИЛКА");

    return 0;
}
