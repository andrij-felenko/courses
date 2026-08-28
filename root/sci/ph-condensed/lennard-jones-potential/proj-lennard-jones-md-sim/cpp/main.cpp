#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <random>
#include <iomanip>

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(double s) const noexcept { return {x * s, y * s, z * s}; }
    Vec3& operator+=(const Vec3& o) noexcept { x += o.x; y += o.y; z += o.z; return *this; }
    Vec3& operator-=(const Vec3& o) noexcept { x -= o.x; y -= o.y; z -= o.z; return *this; }
    Vec3& operator*=(double s) noexcept { x *= s; y *= s; z *= s; return *this; }
    [[nodiscard]] double norm_sq() const noexcept { return x*x + y*y + z*z; }
};

struct Particle {
    Vec3 pos;
    Vec3 vel;
    Vec3 force;
    Vec3 last_pos;
};

struct Pair {
    std::size_t i;
    std::size_t j;
};

class LJSimulationCPP {
public:
    LJSimulationCPP(std::size_t num_particles, double density, double target_temp)
        : num_particles_(num_particles),
          target_temp_(target_temp),
          box_len_(std::cbrt(static_cast<double>(num_particles) / density)),
          particles_(num_particles)
    {
        init_positions_fcc();
        init_velocities();
        rebuild_neighbor_list();
    }

    void run(std::size_t steps, double dt) {
        double pe = compute_forces();

        std::cout << std::setw(8) << "Step"
                  << std::setw(14) << "E_kin/N"
                  << std::setw(14) << "E_pot/N"
                  << std::setw(14) << "E_tot/N"
                  << std::setw(14) << "Temp*" << '\n';

        for (std::size_t step = 0; step <= steps; ++step) {
            // Step 1: Position and half-step velocity update
            for (auto& p : particles_) {
                p.pos += p.vel * dt + p.force * (0.5 * dt * dt);
                p.pos.x -= box_len_ * std::floor(p.pos.x / box_len_);
                p.pos.y -= box_len_ * std::floor(p.pos.y / box_len_);
                p.pos.z -= box_len_ * std::floor(p.pos.z / box_len_);
                p.vel += p.force * (0.5 * dt);
            }

            check_neighbor_rebuild();
            pe = compute_forces();

            // Step 2: Finalize velocity
            double ke = 0.0;
            for (auto& p : particles_) {
                p.vel += p.force * (0.5 * dt);
                ke += 0.5 * p.vel.norm_sq();
            }

            const double inst_temp = (2.0 * ke) / (3.0 * static_cast<double>(num_particles_));
            if (step < 500) {
                apply_berendsen_thermostat(dt, inst_temp);
            }

            if (step % 100 == 0) {
                const double n_inv = 1.0 / static_cast<double>(num_particles_);
                std::cout << std::setw(8) << step
                          << std::setw(14) << std::fixed << std::setprecision(4) << ke * n_inv
                          << std::setw(14) << pe * n_inv
                          << std::setw(14) << (ke + pe) * n_inv
                          << std::setw(14) << inst_temp << '\n';
            }
        }
    }

private:
    void init_positions_fcc() {
        const auto n_side = static_cast<std::size_t>(std::ceil(std::cbrt(num_particles_ / 4.0)));
        const double a = box_len_ / static_cast<double>(n_side);
        std::size_t idx = 0;

        for (std::size_t ix = 0; ix < n_side && idx < num_particles_; ++ix) {
            for (std::size_t iy = 0; iy < n_side && idx < num_particles_; ++iy) {
                for (std::size_t iz = 0; iz < n_side && idx < num_particles_; ++iz) {
                    const Vec3 base{static_cast<double>(ix) * a, static_cast<double>(iy) * a, static_cast<double>(iz) * a};
                    const std::array<Vec3, 4> basis = {{
                        {0.0, 0.0, 0.0},
                        {0.5*a, 0.5*a, 0.0},
                        {0.5*a, 0.0, 0.5*a},
                        {0.0, 0.5*a, 0.5*a}
                    }};
                    for (const auto& b : basis) {
                        if (idx >= num_particles_) break;
                        particles_[idx++].pos = base + b;
                    }
                }
            }
        }
    }

    void init_velocities() {
        std::mt19937_64 rng(42);
        std::uniform_real_distribution<double> dist(-0.5, 0.5);

        Vec3 sum_v;
        for (auto& p : particles_) {
            p.vel = {dist(rng), dist(rng), dist(rng)};
            sum_v += p.vel;
        }

        const Vec3 v_cm = sum_v * (1.0 / static_cast<double>(num_particles_));
        double v2_sum = 0.0;
        for (auto& p : particles_) {
            p.vel -= v_cm;
            v2_sum += p.vel.norm_sq();
        }

        const double current_temp = v2_sum / (3.0 * static_cast<double>(num_particles_));
        const double scale = std::sqrt(target_temp_ / current_temp);
        for (auto& p : particles_) {
            p.vel *= scale;
        }
    }

    [[nodiscard]] Vec3 min_image(const Vec3& dr) const noexcept {
        const double inv_b = 1.0 / box_len_;
        return {
            dr.x - box_len_ * std::round(dr.x * inv_b),
            dr.y - box_len_ * std::round(dr.y * inv_b),
            dr.z - box_len_ * std::round(dr.z * inv_b)
        };
    }

    void rebuild_neighbor_list() {
        neighbor_list_.clear();
        for (std::size_t i = 0; i < num_particles_ - 1; ++i) {
            for (std::size_t j = i + 1; j < num_particles_; ++j) {
                const Vec3 dr = min_image(particles_[i].pos - particles_[j].pos);
                if (dr.norm_sq() < rlist2_) {
                    neighbor_list_.push_back({i, j});
                }
            }
        }
        for (auto& p : particles_) {
            p.last_pos = p.pos;
        }
    }

    void check_neighbor_rebuild() {
        double max_dr2 = 0.0;
        for (const auto& p : particles_) {
            const Vec3 dr = min_image(p.pos - p.last_pos);
            max_dr2 = std::max(max_dr2, dr.norm_sq());
        }
        if (2.0 * std::sqrt(max_dr2) > rskin_) {
            rebuild_neighbor_list();
        }
    }

    [[nodiscard]] double compute_forces() {
        double pe = 0.0;
        for (auto& p : particles_) p.force = {};

        for (const auto& pair : neighbor_list_) {
            auto& p_i = particles_[pair.i];
            auto& p_j = particles_[pair.j];
            const Vec3 dr = min_image(p_i.pos - p_j.pos);
            const double r2 = dr.norm_sq();
            if (r2 < rcut2_) {
                const double inv_r2 = 1.0 / r2;
                const double inv_r6 = inv_r2 * inv_r2 * inv_r2;
                const double f_scalar = 48.0 * inv_r6 * (inv_r6 - 0.5) * inv_r2;

                const Vec3 f_vec = dr * f_scalar;
                p_i.force += f_vec;
                p_j.force -= f_vec;
                pe += 4.0 * inv_r6 * (inv_r6 - 1.0);
            }
        }
        return pe;
    }

    void apply_berendsen_thermostat(double dt, double inst_temp) {
        if (inst_temp <= 1e-10) return;
        const double lam = std::sqrt(1.0 + (dt / tau_temp_) * (target_temp_ / inst_temp - 1.0));
        for (auto& p : particles_) {
            p.vel *= lam;
        }
    }

    std::size_t num_particles_;
    double target_temp_;
    double box_len_;
    static constexpr double rcut_{2.5};
    static constexpr double rskin_{0.3};
    static constexpr double rlist_{rcut_ + rskin_};
    static constexpr double rcut2_{rcut_ * rcut_};
    static constexpr double rlist2_{rlist_ * rlist_};
    static constexpr double tau_temp_{0.1};

    std::vector<Particle> particles_;
    std::vector<Pair> neighbor_list_;
};

int main() {
    LJSimulationCPP sim(256, 0.8442, 0.728);
    sim.run(1000, 0.005);
    return 0;
}
