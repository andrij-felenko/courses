typedef Vec2 (*SupportFn2D)(const void* shape, Vec2 dir);

bool gjk_intersect_2d(const void* shape_a, SupportFn2D sup_a,
                      const void* shape_b, SupportFn2D sup_b) {
    /* 1. Початковий напрямок пошуку (наприклад, вздовж осі X) */
    Vec2 dir = { 1.0f, 0.0f };

    /* 2. Перша точка різниці Мінковського */
    Vec2 p = vec2_sub(sup_a(shape_a, dir), sup_b(shape_b, vec2_neg(dir)));

    Simplex2D simplex = { .count = 0 };
    simplex_push(&simplex, p);

    /* Напрямок до початку координат */
    dir = vec2_neg(p);

    const int MAX_ITERATIONS = 32;
    for (int iter = 0; iter < MAX_ITERATIONS; ++iter) {
        /* Якщо напрямок збігся з нулем, точка лежить рівно на початку координат */
        if (vec2_dot(dir, dir) < 1e-8f) {
            return true;
        }

        /* 3. Опорна точка в новому напрямку */
        p = vec2_sub(sup_a(shape_a, dir), sup_b(shape_b, vec2_neg(dir)));

        /* 4. Перевірка: чи перетнула нова точка площину нуля */
        if (vec2_dot(p, dir) <= 0.0f) {
            /* Фігура A - B не сягає початку координат -> розділені */
            return false;
        }

        /* Додаємо нову точку до симплекса */
        simplex_push(&simplex, p);

        /* 5. Оновлюємо симплекс та обчислюємо наступний напрямок */
        if (handle_simplex(&simplex, &dir)) {
            return true; /* Симплекс містить початок координат -> перетин */
        }
    }

    return false;
}
