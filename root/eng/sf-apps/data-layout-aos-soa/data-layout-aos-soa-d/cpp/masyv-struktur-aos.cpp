#include <vector>
#include <cstdint>

struct alignas(64) Particle {
    float x, y, z;
    float vx, vy, vz;
    float mass;
    float radius;
    int32_t id;
    int32_t flags;
    float pad[2]; // 64 байти
};

std::vector<Particle> particles(1000000);
