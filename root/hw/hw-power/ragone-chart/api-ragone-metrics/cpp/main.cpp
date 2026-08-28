#include <string>
#include <string_view>
#include <cstdint>

// Опис виміряної точки на діаграмі Рагоне (C++17)
struct RagoneDataPoint {
    double discharge_current_a{0.0};     // Струм розряджання (А)
    double terminal_voltage_v{0.0};      // Робоча напруга під навантаженням (В)
    double c_rate{0.0};                  // Кратність розрядного струму (C)
    double specific_power_w_kg{0.0};     // Питома потужність (Вт/кг)
    double specific_energy_wh_kg{0.0};   // Питома енергія (Вт·год/кг)
    double volumetric_power_w_l{0.0};    // Об'ємна потужність (Вт/л)
    double volumetric_energy_wh_l{0.0};  // Об'ємна енергія (Вт·год/л)
    double internal_resistance_ohm{0.0}; // Опір DCIR (Ом)
    double discharge_time_seconds{0.0};  // Час розряджання (с)
    double temperature_celsius{25.0};    // Температура (°C)
    bool cutoff_reached{false};          // Досягнення відсічки
};

// Паспортний опис накопичувального елемента
struct EnergyStorageCell {
    std::string cell_id;                 // Ідентифікатор моделі
    std::string chemistry_type;          // Хімічний тип
    double nominal_voltage_v{3.7};       // Номінальна напруга (В)
    double max_voltage_v{4.2};           // Напруга заряду (В)
    double cutoff_voltage_v{2.8};        // Напруга відсічки (В)
    double capacity_ah{3.0};             // Ємність (А·год)
    double mass_kg{0.048};               // Маса (кг)
    double volume_liters{0.018};         // Об'єм (л)
    double r_internal_dc_ohm{0.025};     // Опір DCIR (Ом)
};
