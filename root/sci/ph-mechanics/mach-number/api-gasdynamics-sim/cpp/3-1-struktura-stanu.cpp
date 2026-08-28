namespace gas_dynamics {

struct isa_atmosphere_state {
    double altitude_m{};          // Геопотенціальна висота над рівнем моря [м]
    double temperature_k{};       // Абсолютна статична температура газу T [К]
    double pressure_pa{};         // Статичний барометричний тиск p [Па]
    double density_kg_m3{};       // Густина повітря ρ [кг/м³]
    double speed_of_sound_m_s{};  // Локальна швидкість звуку a [м/с]
};

} // namespace gas_dynamics
