#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <expected>
#include <cstdint>
#include <cassert>
#include <iomanip>
#include <string_view>

namespace physics::contact {

struct Vec2 {
    float x{0.0f};
    float y{0.0f};

    [[nodiscard]] constexpr Vec2 operator+(Vec2 o) const noexcept { return {x + o.x, y + o.y}; }
    [[nodiscard]] constexpr Vec2 operator-(Vec2 o) const noexcept { return {x - o.x, y - o.y}; }
    [[nodiscard]] constexpr Vec2 operator*(float s) const noexcept { return {x * s, y * s}; }
    [[nodiscard]] constexpr float dot(Vec2 o) const noexcept { return x * o.x + y * o.y; }
    [[nodiscard]] constexpr float cross(Vec2 o) const noexcept { return x * o.y - y * o.x; }
};

struct RigidBody {
    Vec2 pos{};
    Vec2 vel{};
    float ang{0.0f};
    float ang_vel{0.0f};
    float inv_mass{0.0f}; /* 0.0 для статичної опори */
    float inv_inertia{0.0f};
    float width{1.0f};
    float height{1.0f};

    [[nodiscard]] Vec2 point_velocity(Vec2 r) const noexcept {
        return {vel.x - ang_vel * r.y, vel.y + ang_vel * r.x};
    }
};

struct ContactConstraint {
    size_t body_a{0};
    size_t body_b{0};
    Vec2 normal{0.0f, 1.0f};
    Vec2 r_a{};
    Vec2 r_b{};
    float penetration{0.0f};
    float normal_mass{0.0f};
    float bias{0.0f};
    float accumulated_impulse{0.0f};
    uint64_t feature_id{0};

    [[nodiscard]] float normal_force(float dt) const noexcept {
        return (dt > 0.0f) ? (accumulated_impulse / dt) : 0.0f;
    }
};

class ContactPhysicsWorld {
public:
    Vec2 gravity{0.0f, -9.8f};
    float linear_slop{0.005f};     // 5 мм
    float baumgarte_factor{0.2f};  // 20% виправлення перекриття за кадр

    size_t add_body(Vec2 position, float mass, float w, float h) {
        RigidBody b{};
        b.pos = position;
        b.width = w;
        b.height = h;

        if (mass > 0.0f) {
            b.inv_mass = 1.0f / mass;
            const float i = (1.0f / 12.0f) * mass * (w * w + h * h);
            b.inv_inertia = (i > 0.0f) ? (1.0f / i) : 0.0f;
        } else {
            b.inv_mass = 0.0f;
            b.inv_inertia = 0.0f;
        }

        bodies_.push_back(b);
        return bodies_.size() - 1;
    }

    size_t add_contact(size_t a, size_t b, Vec2 normal, Vec2 r_a, Vec2 r_b, 
                       float depth, uint64_t id = 0) 
    {
        ContactConstraint c{};
        c.body_a = a;
        c.body_b = b;
        c.normal = normal;
        c.r_a = r_a;
        c.r_b = r_b;
        c.penetration = depth;
        c.feature_id = id;
        c.accumulated_impulse = 0.0f;

        contacts_.push_back(c);
        return contacts_.size() - 1;
    }

    void step(float dt, int iterations) noexcept {
        // 1. Вільний крок швидкостей від гравітації
        for (auto& b : bodies_) {
            if (b.inv_mass > 0.0f) {
                b.vel = b.vel + gravity * dt;
            }
        }

        // 2. Prestep: ефективні маси та теплий старт
        prestep(dt);

        // 3. Projected Gauss-Seidel ітератор
        for (int i = 0; i < iterations; ++i) {
            solve_velocities();
        }

        // 4. Оновлення положень
        for (auto& b : bodies_) {
            b.pos = b.pos + b.vel * dt;
            b.ang += b.ang_vel * dt;
        }
    }

    [[nodiscard]] std::span<const ContactConstraint> contacts() const noexcept {
        return contacts_;
    }

    [[nodiscard]] std::span<const RigidBody> bodies() const noexcept {
        return bodies_;
    }

    [[nodiscard]] std::span<RigidBody> bodies_mut() noexcept {
        return bodies_;
    }

private:
    std::vector<RigidBody> bodies_;
    std::vector<ContactConstraint> contacts_;

    static void apply_impulse(RigidBody& a, RigidBody& b, const ContactConstraint& c, float dl) noexcept {
        const Vec2 p = c.normal * dl;
        a.vel = a.vel + p * a.inv_mass;
        a.ang_vel += a.inv_inertia * c.r_a.cross(p);

        b.vel = b.vel - p * b.inv_mass;
        b.ang_vel -= b.inv_inertia * c.r_b.cross(p);
    }

    void prestep(float dt) noexcept {
        for (auto& c : contacts_) {
            auto& a = bodies_[c.body_a];
            auto& b = bodies_[c.body_b];

            const float rn_a = c.r_a.cross(c.normal);
            const float rn_b = c.r_b.cross(c.normal);
            const float k = a.inv_mass + b.inv_mass +
                            a.inv_inertia * rn_a * rn_a + b.inv_inertia * rn_b * rn_b;

            c.normal_mass = (k > 0.0f) ? (1.0f / k) : 0.0f;

            const float pen_excess = std::max(0.0f, c.penetration - linear_slop);
            c.bias = (baumgarte_factor / dt) * pen_excess;

            // Теплий старт
            apply_impulse(a, b, c, c.accumulated_impulse);
        }
    }

    void solve_velocities() noexcept {
        for (auto& c : contacts_) {
            auto& a = bodies_[c.body_a];
            auto& b = bodies_[c.body_b];

            const Vec2 va = a.point_velocity(c.r_a);
            const Vec2 vb = b.point_velocity(c.r_b);
            const Vec2 dv = va - vb;

            const float vn = dv.dot(c.normal);
            const float dl = c.normal_mass * (c.bias - vn);

            // Проєкція на область невід'ємних поштовхів (PGS clamping)
            const float old_imp = c.accumulated_impulse;
            c.accumulated_impulse = std::max(0.0f, old_imp + dl);
            const float delta_to_apply = c.accumulated_impulse - old_imp;

            apply_impulse(a, b, c, delta_to_apply);
        }
    }
};

} // namespace physics::contact

// ==================== АВТОМАТИЗОВАНІ ТЕСТИ C++20 ====================

int main() {
    using namespace physics::contact;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "================ ЗАПУСК ТЕСТІВ КОНТАКТНОГО РОЗВ'ЯЗУВАЧА (C++20) ================\n";

    // Тест 1: Статичний ящик 6 кг
    {
        ContactPhysicsWorld world;
        const auto ground = world.add_body({0.0f, 0.0f}, 0.0f, 10.0f, 0.5f);
        const auto box = world.add_body({0.0f, 0.5f}, 6.0f, 0.4f, 0.4f);

        constexpr float dt = 1.0f / 60.0f;
        world.add_contact(box, ground, {0.0f, 1.0f}, {0.0f, -0.2f}, {0.0f, 0.25f}, 0.005f, 101);

        for (int frame = 0; frame < 60; ++frame) {
            world.step(dt, 10);
        }

        const float force = world.contacts()[0].normal_force(dt);
        std::cout << "[C++20] Тест 1 (Ящик 6 кг):        N = " << force << " Н (очікувано 58.80 Н)\n";
        assert(std::abs(force - 58.80f) < 0.05f);
    }

    // Тест 2: Похила площина 30 градусів
    {
        ContactPhysicsWorld world;
        const auto ground = world.add_body({0.0f, 0.0f}, 0.0f, 10.0f, 0.5f);
        const auto box = world.add_body({0.0f, 1.0f}, 6.0f, 0.4f, 0.4f);

        constexpr float dt = 1.0f / 60.0f;
        const Vec2 slope_normal{-0.5f, 0.8660254f};
        world.add_contact(box, ground, slope_normal, {0.0f, 0.0f}, {0.0f, 0.0f}, 0.005f, 202);

        world.step(dt, 10);
        const float force = world.contacts()[0].normal_force(dt);
        constexpr float expected = 6.0f * 9.8f * 0.8660254f;
        std::cout << "[C++20] Тест 2 (Схил 30°):         N = " << force << " Н (очікувано " << expected << " Н)\n";
        assert(std::abs(force - expected) < 0.05f);
    }

    // Тест 3: Стос із трьох ящиків
    {
        ContactPhysicsWorld world;
        const auto ground = world.add_body({0.0f, 0.0f}, 0.0f, 10.0f, 0.5f);
        const auto b0 = world.add_body({0.0f, 0.5f}, 1.0f, 0.4f, 0.4f);
        const auto b1 = world.add_body({0.0f, 1.0f}, 1.0f, 0.4f, 0.4f);
        const auto b2 = world.add_body({0.0f, 1.5f}, 1.0f, 0.4f, 0.4f);

        constexpr float dt = 1.0f / 60.0f;
        world.add_contact(b0, ground, {0.0f, 1.0f}, {0.0f, -0.2f}, {0.0f, 0.25f}, 0.005f, 301);
        world.add_contact(b1, b0,     {0.0f, 1.0f}, {0.0f, -0.2f}, {0.0f, 0.2f},  0.005f, 302);
        world.add_contact(b2, b1,     {0.0f, 1.0f}, {0.0f, -0.2f}, {0.0f, 0.2f},  0.005f, 303);

        for (int frame = 0; frame < 10; ++frame) {
            world.step(dt, 8);
        }

        const auto cts = world.contacts();
        std::cout << "[C++20] Тест 3 (Стос 3x1 кг):      N0 = " << cts[0].normal_force(dt)
                  << " Н, N1 = " << cts[1].normal_force(dt)
                  << " Н, N2 = " << cts[2].normal_force(dt) << " Н\n";

        assert(std::abs(cts[0].normal_force(dt) - 29.40f) < 0.05f);
        assert(std::abs(cts[1].normal_force(dt) - 19.60f) < 0.05f);
        assert(std::abs(cts[2].normal_force(dt) - 9.80f) < 0.05f);
    }

    std::cout << "УСІ ТЕСТИ C++20 УСПІШНО ПРОЙДЕНО!\n";
    return 0;
}
