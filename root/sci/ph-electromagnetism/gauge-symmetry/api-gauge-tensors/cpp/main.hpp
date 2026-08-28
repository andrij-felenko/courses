#pragma once
#include <vector>
#include <cstddef>

enum class GaugeChoice {
    Lorentz,
    Coulomb,
    Temporal,
    Axial
};

struct FieldGridConfig {
    std::size_t nx, ny, nz;
    double dx, dy, dz;
    double dt;
    GaugeChoice gauge;
};

struct FieldValues {
    std::vector<double> phi;
    std::vector<double> Ax, Ay, Az;
    std::vector<double> Ex, Ey, Ez;
    std::vector<double> Bx, By, Bz;
};

class IGaugeSolver {
public:
    virtual ~IGaugeSolver() = default;
    virtual void set_sources(const std::vector<double>& rho,
                            const std::vector<double>& Jx,
                            const std::vector<double>& Jy,
                            const std::vector<double>& Jz) = 0;
    virtual void step_time() = 0;
    virtual void apply_gauge_fixing() = 0;
    virtual FieldValues get_fields() const = 0;
};
