/**
 * @file acoustics_api.hpp
 * @brief Modern C++20 header-only wrapper for acoustic property computations
 */

#pragma once

#include <expected>
#include <string_view>
#include <span>
#include <array>
#include <concepts>

namespace acoustics::api {

enum class Status : int32_t {
    Success = 0,
    NullPointer = -101,
    OutOfRange = -102,
    MathDomain = -103
};

struct MaterialSpec {
    std::string_view name;
    double density_kg_m3;
    double longitudinal_speed_m_s;
    double transverse_speed_m_s;
    
    [[nodiscard]] constexpr double specific_impedance() const noexcept {
        return density_kg_m3 * longitudinal_speed_m_s;
    }
};

class MaterialDatabase {
public:
    [[nodiscard]] static constexpr std::expected<MaterialSpec, Status> 
    find_by_name(std::string_view name) noexcept {
        for (const auto& mat : kStandardMaterials) {
            if (mat.name == name) {
                return mat;
            }
        }
        return std::unexpected(Status::OutOfRange);
    }

    [[nodiscard]] static constexpr std::span<const MaterialSpec> 
    all_materials() noexcept {
        return kStandardMaterials;
    }

private:
    static constexpr std::array<MaterialSpec, 6> kStandardMaterials{{
        {"Air_20C", 1.204, 343.2, 0.0},
        {"Water_20C", 998.2, 1482.3, 0.0},
        {"Seawater_20C", 1025.0, 1522.0, 0.0},
        {"Aluminum_D16", 2700.0, 6320.0, 3130.0},
        {"Steel_Structural", 7850.0, 5940.0, 3220.0},
        {"Diamond_C", 3520.0, 18000.0, 12300.0}
    }};
};

} // namespace acoustics::api
