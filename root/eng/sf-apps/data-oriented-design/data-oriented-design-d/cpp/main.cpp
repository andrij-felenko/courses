#include <vector>
#include <span>
#include <memory>
#include <string>

// =========================================================================
// 1. Класичний об'єктний підхід (AoS)
// =========================================================================
class IEntity {
public:
    virtual ~IEntity() = default;
    virtual void update(float dt) = 0;
};

class Monster : public IEntity {
public:
    void update(float dt) override {
        x_ += vx_ * dt;
        y_ += vy_ * dt;
        z_ += vz_ * dt;
    }
private:
    float x_{0}, y_{0}, z_{0};
    float vx_{1}, vy_{1}, vz_{1};
    std::string name_{"Goblin"};
    int health_{100};
};

void update_entities_oop(std::span<const std::unique_ptr<IEntity>> entities, float dt) {
    for (const auto& entity : entities) {
        entity->update(dt); // Віртуальний виклик + розіменування вказівника
    }
}

// =========================================================================
// 2. Data-Oriented Design (SoA)
// =========================================================================
struct PositionStream {
    std::vector<float> x;
    std::vector<float> y;
    std::vector<float> z;
};

struct VelocityStream {
    std::vector<float> vx;
    std::vector<float> vy;
    std::vector<float> vz;
};

void update_entities_dod(PositionStream& pos, const VelocityStream& vel, float dt) noexcept {
    const std::size_t n = pos.x.size();
    float* __restrict px = pos.x.data();
    float* __restrict py = pos.y.data();
    float* __restrict pz = pos.z.data();
    const float* __restrict pvx = vel.vx.data();
    const float* __restrict pvy = vel.vy.data();
    const float* __restrict pvz = vel.vz.data();

    #pragma omp simd
    for (std::size_t i = 0; i < n; ++i) {
        px[i] += pvx[i] * dt;
        py[i] += pvy[i] * dt;
        pz[i] += pvz[i] * dt;
    }
}
