// dielectric_materials.hpp — Специфікація тензорів матеріалів для C++20 солверів
#ifndef DIELECTRIC_MATERIALS_HPP
#define DIELECTRIC_MATERIALS_HPP

#include <string>
#include <array>
#include <variant>
#include <optional>
#include <span>

namespace Physics::EM {

enum class CrystalSystem {
    Isotropic,
    Uniaxial,
    Biaxial,
    Ferroelectric
};

using Tensor3x3 = std::array<std::array<double, 3>, 3>;

struct DielectricMaterialSpec {
    std::string name;
    CrystalSystem system{CrystalSystem::Isotropic};
    Tensor3x3 eps_r{ {{{1.0, 0.0, 0.0}}, {{0.0, 1.0, 0.0}}, {{0.0, 0.0, 1.0}}} };
    double loss_tangent{0.0};
    double breakdown_field_V_per_m{3.0e6};
    std::optional<double> remanent_polarization_C_per_m2;

    [[nodiscard]] static DielectricMaterialSpec create_isotropic(std::string name, double eps_r, double loss_tan = 0.0) {
        DielectricMaterialSpec m;
        m.name = std::move(name);
        m.system = CrystalSystem::Isotropic;
        m.loss_tangent = loss_tan;
        m.eps_r = {{{ {eps_r, 0.0, 0.0}}, {{0.0, eps_r, 0.0}}, {{0.0, 0.0, eps_r}} }};
        return m;
    }

    [[nodiscard]] static DielectricMaterialSpec create_uniaxial(std::string name, double eps_perp, double eps_para) {
        DielectricMaterialSpec m;
        m.name = std::move(name);
        m.system = CrystalSystem::Uniaxial;
        m.eps_r = {{{ {eps_perp, 0.0, 0.0}}, {{0.0, eps_perp, 0.0}}, {{0.0, 0.0, eps_para}} }};
        return m;
    }

    [[nodiscard]] std::array<double, 3> compute_D(const std::array<double, 3>& E, double eps0 = 8.854187817e-12) const noexcept {
        std::array<double, 3> D{0.0, 0.0, 0.0};
        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                D[i] += eps0 * eps_r[i][j] * E[j];
            }
        }
        return D;
    }
};

} // namespace Physics::EM

#endif // DIELECTRIC_MATERIALS_HPP
