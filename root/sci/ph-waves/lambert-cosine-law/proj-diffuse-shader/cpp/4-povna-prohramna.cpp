// C++20 Implementation: Modern Lambertian Shader and Monte Carlo Sampler
#include <iostream>
#include <cmath>
#include <numbers>
#include <array>
#include <random>
#include <span>
#include <concepts>

namespace optics {

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vec3 operator+(const Vec3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr Vec3 operator-(const Vec3& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    constexpr Vec3 operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    [[nodiscard]] constexpr double dot(const Vec3& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }

    [[nodiscard]] Vec3 normalized() const noexcept {
        const double len = std::sqrt(dot(*this));
        if (len < 1e-12) return {0.0, 0.0, 0.0};
        return {x / len, y / len, z / len};
    }

    [[nodiscard]] constexpr Vec3 cross(const Vec3& rhs) const noexcept {
        return {
            y * rhs.z - z * rhs.y,
            z * rhs.x - x * rhs.z,
            x * rhs.y - y * rhs.x
        };
    }
};

struct ColorRGB {
    double r{0.0}, g{0.0}, b{0.0};

    constexpr ColorRGB operator*(const ColorRGB& rhs) const noexcept {
        return {r * rhs.r, g * rhs.g, b * rhs.b};
    }
    constexpr ColorRGB operator*(double scalar) const noexcept {
        return {r * scalar, g * scalar, b * scalar};
    }
};

// Обчислення ламбертової BRDF з перевіркою альбедо на етапі компіляції або виконання
constexpr double lambert_brdf(double albedo) noexcept {
    return albedo / std::numbers::pi;
}

// Функтор ламбертового розсіювання для масиву точок
class LambertShader {
public:
    explicit constexpr LambertShader(ColorRGB albedo) noexcept : albedo_{albedo} {}

    [[nodiscard]] ColorRGB evaluate(const Vec3& point, const Vec3& normal,
                                   const Vec3& light_pos, const ColorRGB& light_power) const noexcept {
        const Vec3 light_vec = light_pos - point;
        const double dist_sq = light_vec.dot(light_vec);
        const Vec3 L = light_vec.normalized();
        const Vec3 N = normal.normalized();

        const double NdotL = std::max(0.0, N.dot(L));
        const double attenuation = 1.0 / (dist_sq + 1e-6);

        const ColorRGB brdf{
            albedo_.r / std::numbers::pi,
            albedo_.g / std::numbers::pi,
            albedo_.b / std::numbers::pi
        };

        return brdf * light_power * NdotL * attenuation;
    }

private:
    ColorRGB albedo_;
};

// Генератор косинусно-зважених напрямків для трасування шляхів (Path Tracing)
class CosineHemisphereSampler {
public:
    CosineHemisphereSampler() : rng_{std::random_device{}()}, dist_{0.0, 1.0} {}

    [[nodiscard]] Vec3 sample(const Vec3& normal) noexcept {
        const double u1 = dist_(rng_);
        const double u2 = dist_(rng_);

        const double r = std::sqrt(u1);
        const double phi = 2.0 * std::numbers::pi * u2;

        const double x = r * std::cos(phi);
        const double y = r * std::sin(phi);
        const double z = std::sqrt(std::max(0.0, 1.0 - u1));

        const Vec3 N = normal.normalized();
        const Vec3 up = (std::abs(N.z) < 0.999) ? Vec3{0.0, 0.0, 1.0} : Vec3{1.0, 0.0, 0.0};
        const Vec3 T = up.cross(N).normalized();
        const Vec3 B = N.cross(T);

        return (T * x + B * y + N * z).normalized();
    }

private:
    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_;
};

} // namespace optics

int main() {
    using namespace optics;

    constexpr Vec3 point{0.0, 0.0, 0.0};
    constexpr Vec3 normal{0.0, 0.0, 1.0};
    constexpr Vec3 light_pos{2.0, 2.0, 3.0};
    constexpr ColorRGB light_intensity{100.0, 100.0, 100.0};

    constexpr LambertShader shader{ColorRGB{0.8, 0.8, 0.8}};
    const ColorRGB result = shader.evaluate(point, normal, light_pos, light_intensity);

    std::cout << "C++ Lambert Diffuse Color: R=" << result.r
              << ", G=" << result.g
              << ", B=" << result.b << '\n';

    CosineHemisphereSampler sampler;
    const Vec3 sampled_dir = sampler.sample(normal);
    std::cout << "Sampled Direction: (" << sampled_dir.x << ", "
              << sampled_dir.y << ", " << sampled_dir.z << ")\n";

    return 0;
}
