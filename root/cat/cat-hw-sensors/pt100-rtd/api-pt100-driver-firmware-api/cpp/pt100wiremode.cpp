#include <cstdint>

enum class Pt100WireMode : uint8_t {
    TwoWire = 2,    // 2-провідне підключення
    ThreeWire = 3,  // 3-провідне підключення
    FourWire = 4    // 4-провідне підключення Кельвіна
};

struct Pt100Config {
    Pt100WireMode wire_mode{Pt100WireMode::FourWire};
    float r_ref_ohms{400.0f};           // Опір еталонного резистора R_ref
    float r_0_ohms{100.0f};             // Опір сенсора при 0 °C
    uint16_t excitation_current_ua{250};// Струм збудження в мкА
    float alpha_coef{0.003851f};        // Коефіцієнт α (DIN/IEC 60751)
    float filter_alpha{0.2f};           // Згладжування експоненційного фільтра
};
