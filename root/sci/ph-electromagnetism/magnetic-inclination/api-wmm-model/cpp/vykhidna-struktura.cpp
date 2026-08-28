/* cpp */
namespace navigation::wmm {

struct WmmElements {
    double north_component_nT{0.0};  // X: Північна складова [нТл]
    double east_component_nT{0.0};   // Y: Східна складова [нТл]
    double down_component_nT{0.0};   // Z: Вертикальна складова [нТл]
    double horizontal_nT{0.0};       // H: Горизонтальна складова [нТл]
    double total_intensity_nT{0.0};  // F: Повний модуль індукції [нТл]
    double inclination_deg{0.0};     // I: Кут магнітного нахилу [градуси]
    double declination_deg{0.0};     // D: Кут магнітного схилення [градуси]
    double grid_variation_deg{0.0};  // GV: Грідовий азимут [градуси]
};

} // namespace navigation::wmm
