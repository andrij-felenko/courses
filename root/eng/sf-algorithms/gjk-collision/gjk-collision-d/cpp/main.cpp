#include <array>
#include <cmath>
#include <span>
#include <concepts>

struct Vec3 {
    float x{0.0f}, y{0.0f}, z{0.0f};

    constexpr Vec3 operator+(Vec3 r) const noexcept { return {x + r.x, y + r.y, z + r.z}; }
    constexpr Vec3 operator-(Vec3 r) const noexcept { return {x - r.x, y - r.y, z - r.z}; }
    constexpr Vec3 operator-() const noexcept { return {-x, -y, -z}; }
    constexpr float dot(Vec3 r) const noexcept { return x * r.x + y * r.y + z * r.z; }

    constexpr Vec3 cross(Vec3 r) const noexcept {
        return {
            y * r.z - z * r.y,
            z * r.x - x * r.z,
            x * r.y - y * r.x
        };
    }
};

class Simplex3D {
public:
    std::array<Vec3, 4> points{};
    int count{0};

    void push_front(Vec3 p) noexcept {
        points[3] = points[2];
        points[2] = points[1];
        points[1] = points[0];
        points[0] = p;
        if (count < 4) ++count;
    }

    bool solve(Vec3& dir) noexcept {
        if (count == 2) return solve_line(dir);
        if (count == 3) return solve_triangle(dir);
        if (count == 4) return solve_tetrahedron(dir);
        return false;
    }

private:
    bool solve_line(Vec3& dir) noexcept {
        Vec3 a = points[0], b = points[1];
        Vec3 ab = b - a, ao = -a;

        if (ab.dot(ao) > 0.0f) {
            dir = ab.cross(ao).cross(ab);
            if (dir.dot(dir) < 1e-8f) {
                Vec3 axis = (std::abs(ab.x) > 0.9f) ? Vec3{0, 1, 0} : Vec3{1, 0, 0};
                dir = ab.cross(axis);
            }
        } else {
            points[0] = a;
            count = 1;
            dir = ao;
        }
        return false;
    }

    bool solve_triangle(Vec3& dir) noexcept {
        Vec3 a = points[0], b = points[1], c = points[2];
        Vec3 ab = b - a, ac = c - a, ao = -a;
        Vec3 abc = ab.cross(ac);

        Vec3 ab_perp = ab.cross(abc);
        Vec3 ac_perp = abc.cross(ac);

        if (ab_perp.dot(ao) > 0.0f) {
            points[0] = a; points[1] = b; count = 2;
            return solve_line(dir);
        }
        if (ac_perp.dot(ao) > 0.0f) {
            points[0] = a; points[1] = c; count = 2;
            return solve_line(dir);
        }

        if (abc.dot(ao) > 0.0f) {
            dir = abc;
        } else {
            points[1] = c;
            points[2] = b;
            dir = -abc;
        }
        return false;
    }

    bool solve_tetrahedron(Vec3& dir) noexcept {
        Vec3 a = points[0], b = points[1], c = points[2], d = points[3];
        Vec3 ab = b - a, ac = c - a, ad = d - a, ao = -a;

        Vec3 abc = ab.cross(ac);
        Vec3 acd = ac.cross(ad);
        Vec3 adb = ad.cross(ab);

        if (abc.dot(ao) > 0.0f) {
            points[0] = a; points[1] = b; points[2] = c; count = 3;
            return solve_triangle(dir);
        }
        if (acd.dot(ao) > 0.0f) {
            points[0] = a; points[1] = c; points[2] = d; count = 3;
            return solve_triangle(dir);
        }
        if (adb.dot(ao) > 0.0f) {
            points[0] = a; points[1] = d; points[2] = b; count = 3;
            return solve_triangle(dir);
        }
        return true;
    }
};

template <typename ShapeA, typename ShapeB, typename SupA, typename SupB>
bool gjk_intersect_3d(const ShapeA& a, SupA sup_a,
                      const ShapeB& b, SupB sup_b) noexcept {
    Vec3 dir{0.0f, 1.0f, 0.0f};
    Vec3 p = sup_a(a, dir) - sup_b(b, -dir);

    Simplex3D simplex;
    simplex.push_front(p);
    dir = -p;

    for (int iter = 0; iter < 40; ++iter) {
        if (dir.dot(dir) < 1e-8f) return true;

        p = sup_a(a, dir) - sup_b(b, -dir);
        if (p.dot(dir) <= 0.0f) return false;

        simplex.push_front(p);
        if (simplex.solve(dir)) return true;
    }
    return false;
}
