/* cpp */
#include <array>

namespace navigation {

struct MagnetometerCalibration {
    // Вектор зсуву твердого заліза (Hard-Iron Bias, [мкТл])
    std::array<float, 3> hard_iron_bias{0.0f, 0.0f, 0.0f};
    
    // 3x3 симетрична матриця масштабу й повороту м'якого заліза (Soft-Iron Matrix)
    std::array<std::array<float, 3>, 3> soft_iron_matrix{{{1.0f, 0.0f, 0.0f},
                                                         {0.0f, 1.0f, 0.0f},
                                                         {0.0f, 0.0f, 1.0f}}};
    
    float expected_total_field_uT{50.0f};
    float expected_inclination_deg{67.0f};
};

} // namespace navigation
