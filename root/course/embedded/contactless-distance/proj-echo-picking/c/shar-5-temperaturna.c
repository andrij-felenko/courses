// Швидкість звуку з поправкою на температуру (°C → м/с).
static inline float sound_speed(float t_celsius) {
    return 331.3f + 0.606f * t_celsius;
}

// Час польоту (мкс) → відстань (м) з ЖИВОЮ швидкістю, з двійкою за шлях туди-й-назад.
static inline float tof_to_distance_m(uint32_t echo_us, float t_celsius) {
    float v = sound_speed(t_celsius);          // жива v, не константа!
    return v * (echo_us * 1e-6f) * 0.5f;       // d = v·t/2
}
