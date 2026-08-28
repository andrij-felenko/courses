typedef struct {
    Vec2 points[3];
    int count;
} Simplex2D;

static inline void simplex_push(Simplex2D* s, Vec2 p) {
    /* Зсуваємо наявні вершини, щоб нова вершина завжди була points[0] */
    s->points[2] = s->points[1];
    s->points[1] = s->points[0];
    s->points[0] = p;
    if (s->count < 3) {
        s->count++;
    }
}

/* Обробка відрізка (2 точки) */
static inline bool handle_line_simplex(Simplex2D* s, Vec2* dir) {
    Vec2 a = s->points[0];
    Vec2 b = s->points[1];
    Vec2 ab = vec2_sub(b, a);
    Vec2 ao = vec2_neg(a);

    /* d = (AB × AO) × AB */
    *dir = vec2_triple_product(ab, ao, ab);
    if (vec2_dot(*dir, *dir) < 1e-8f) {
        /* Якщо AO колінеарний AB, обираємо перпендикуляр за годинниковою стрілкою */
        *dir = (Vec2){ -ab.y, ab.x };
    }
    return false; /* Перетин ще не зафіксовано */
}

/* Обробка трикутника (3 точки) */
static inline bool handle_triangle_simplex(Simplex2D* s, Vec2* dir) {
    Vec2 a = s->points[0];
    Vec2 b = s->points[1];
    Vec2 c = s->points[2];

    Vec2 ab = vec2_sub(b, a);
    Vec2 ac = vec2_sub(c, a);
    Vec2 ao = vec2_neg(a);

    /* Обчислення зовнішніх нормалей */
    Vec2 ab_perp = vec2_triple_product(ac, ab, ab);
    Vec2 ac_perp = vec2_triple_product(ab, ac, ac);

    /* Перевірка зони Вороного ребра AB */
    if (vec2_dot(ab_perp, ao) > 0.0f) {
        s->points[0] = a;
        s->points[1] = b;
        s->count = 2;
        *dir = ab_perp;
        return false;
    }

    /* Перевірка зони Вороного ребра AC */
    if (vec2_dot(ac_perp, ao) > 0.0f) {
        s->points[0] = a;
        s->points[1] = c;
        s->count = 2;
        *dir = ac_perp;
        return false;
    }

    /* Початок координат усередині трикутника ABC -> КОЛІЗІЯ */
    return true;
}

static inline bool handle_simplex(Simplex2D* s, Vec2* dir) {
    if (s->count == 2) {
        return handle_line_simplex(s, dir);
    }
    if (s->count == 3) {
        return handle_triangle_simplex(s, dir);
    }
    return false;
}
