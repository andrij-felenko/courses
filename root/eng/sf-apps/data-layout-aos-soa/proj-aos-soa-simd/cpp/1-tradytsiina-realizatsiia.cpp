#include <vector>
#include <span>
#include <algorithm>
#include <cstdint>

struct alignas(16) ParticleAoS {
    float x, y, z;
    float vx, vy, vz;
    float mass;
    float radius;
    int32_t id;
    int32_t flags;
    float pad[2]; // 48 байтів на структуру
};

void update_particles_aos(std::span<ParticleAoS> particles, float dt, float damping, float min_b, float max_b) noexcept
{
    for (auto &p : particles) {
        p.vx *= damping;
        p.vy *= damping;
        p.vz *= damping;

        p.x = std::clamp(p.x + p.vx * dt, min_b, max_b);
        p.y = std::clamp(p.y + p.vy * dt, min_b, max_b);
        p.z = std::clamp(p.z + p.vz * dt, min_b, max_b);
    }
}
