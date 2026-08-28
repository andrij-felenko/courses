#include <iostream>
#include <cmath>
#include <vector>
#include <algorithm>
#include <iomanip>

struct Vector3 {
    double x{0.0}, y{0.0}, z{0.0};

    double dot(const Vector3& o) const {
        return x * o.x + y * o.y + z * o.z;
    }

    double length() const {
        return std::sqrt(dot(*this));
    }

    Vector3 normalize() const {
        double l = length();
        if (l == 0.0) return {0.0, 0.0, 0.0};
        return {x / l, y / l, z / l};
    }

    Vector3 operator+(const Vector3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vector3 operator-(const Vector3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vector3 operator*(double s) const { return {x * s, y * s, z * s}; }
    Vector3 operator-() const { return {-x, -y, -z}; }
};

struct MirrorPlane {
    Vector3 point;
    Vector3 normal;

    MirrorPlane(Vector3 p, Vector3 n) : point(p), normal(n.normalize()) {}

    bool intersect(const Vector3& ray_pos, const Vector3& ray_dir, double& out_t) const {
        double denom = ray_dir.dot(normal);
        if (std::abs(denom) < 1e-9) return false;
        double t = (point - ray_pos).dot(normal) / denom;
        if (t > 1e-6) {
            out_t = t;
            return true;
        }
        return false;
    }
};

Vector3 reflect(const Vector3& v, const Vector3& n) {
    return v - n * (2.0 * v.dot(n));
}

int main() {
    std::vector<MirrorPlane> mirrors = {
        MirrorPlane({0.0, 0.0, 0.0}, {1.0, 0.0, 0.0}),
        MirrorPlane({0.0, 0.0, 0.0}, {0.0, 1.0, 0.0}),
        MirrorPlane({0.0, 0.0, 0.0}, {0.0, 0.0, 1.0})
    };

    Vector3 v_in = Vector3{-1.0, -1.0, -1.0}.normalize();
    Vector3 p_in{2.0, 1.5, 1.8};

    Vector3 cur_pos = p_in;
    Vector3 cur_dir = v_in;
    int last_idx = -1;

    for (int bounce = 0; bounce < 3; ++bounce) {
        double best_t = 1e9;
        int hit_idx = -1;

        for (size_t i = 0; i < mirrors.size(); ++i) {
            if (static_cast<int>(i) == last_idx) continue;
            double t = 0.0;
            if (mirrors[i].intersect(cur_pos, cur_dir, t)) {
                if (t < best_t) {
                    best_t = t;
                    hit_idx = static_cast<int>(i);
                }
            }
        }

        if (hit_idx == -1) break;

        cur_pos = cur_pos + cur_dir * best_t;
        cur_dir = reflect(cur_dir, mirrors[hit_idx].normal);
        last_idx = hit_idx;
    }

    Vector3 target = -v_in;
    double cos_a = std::clamp(cur_dir.dot(target), -1.0, 1.0);
    double dev_arcsec = std::acos(cos_a) * (180.0 / M_PI) * 3600.0;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Вхідний напрямок: (" << v_in.x << ", " << v_in.y << ", " << v_in.z << ")\n";
    std::cout << "Вихідний напрямок: (" << cur_dir.x << ", " << cur_dir.y << ", " << cur_dir.z << ")\n";
    std::cout << "Кутове відхилення: " << dev_arcsec << " кутових секунд\n";

    return 0;
}
