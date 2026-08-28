// Ідіоматична C++ функція компенсації мертвого часу
template <typename PhaseArray>
constexpr void apply_dead_time_compensation(PhaseArray& voltages,
                                           const PhaseArray& currents,
                                           float dt_voltage,
                                           float threshold) noexcept {
    for (size_t i = 0; i < voltages.size(); ++i) {
        if (currents[i] > threshold) {
            voltages[i] += dt_voltage;
        } else if (currents[i] < -threshold) {
            voltages[i] -= dt_voltage;
        }
    }
}
