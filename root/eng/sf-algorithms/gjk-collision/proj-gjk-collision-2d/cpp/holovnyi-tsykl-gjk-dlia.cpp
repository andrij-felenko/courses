template <typename ShapeA, typename ShapeB, typename SupA, typename SupB>
bool gjk_intersect_2d(const ShapeA& shape_a, SupA sup_a,
                      const ShapeB& shape_b, SupB sup_b) noexcept {
    Vec2 dir{1.0f, 0.0f};

    Vec2 p = sup_a(shape_a, dir) - sup_b(shape_b, -dir);

    Simplex2D simplex;
    simplex.push_front(p);

    dir = -p;

    constexpr int max_iterations = 32;
    for (int iter = 0; iter < max_iterations; ++iter) {
        if (dir.dot(dir) < 1e-8f) {
            return true;
        }

        p = sup_a(shape_a, dir) - sup_b(shape_b, -dir);

        if (p.dot(dir) <= 0.0f) {
            return false;
        }

        simplex.push_front(p);

        if (simplex.solve(dir)) {
            return true;
        }
    }

    return false;
}
