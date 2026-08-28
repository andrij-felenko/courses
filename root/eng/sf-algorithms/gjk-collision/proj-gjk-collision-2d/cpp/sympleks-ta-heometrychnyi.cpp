class Simplex2D {
public:
    std::array<Vec2, 3> points{};
    int count{0};

    void push_front(Vec2 p) noexcept {
        points[2] = points[1];
        points[1] = points[0];
        points[0] = p;
        if (count < 3) ++count;
    }

    bool solve(Vec2& dir) noexcept {
        if (count == 2) {
            Vec2 a = points[0];
            Vec2 b = points[1];
            Vec2 ab = b - a;
            Vec2 ao = -a;

            dir = ab.triple_product(ao, ab);
            if (dir.dot(dir) < 1e-8f) {
                dir = {-ab.y, ab.x};
            }
            return false;
        }

        if (count == 3) {
            Vec2 a = points[0];
            Vec2 b = points[1];
            Vec2 c = points[2];

            Vec2 ab = b - a;
            Vec2 ac = c - a;
            Vec2 ao = -a;

            Vec2 ab_perp = ac.triple_product(ab, ab);
            Vec2 ac_perp = ab.triple_product(ac, ac);

            if (ab_perp.dot(ao) > 0.0f) {
                points[0] = a;
                points[1] = b;
                count = 2;
                dir = ab_perp;
                return false;
            }

            if (ac_perp.dot(ao) > 0.0f) {
                points[0] = a;
                points[1] = c;
                count = 2;
                dir = ac_perp;
                return false;
            }

            /* Початок координат усередині трикутника */
            return true;
        }
        return false;
    }
};
