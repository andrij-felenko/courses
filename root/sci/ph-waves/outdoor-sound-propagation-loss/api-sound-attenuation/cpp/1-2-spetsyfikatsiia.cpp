namespace acoustic {

enum class Status : int32_t {
    Success = 0,
    InvalidPointer = -1,
    FrequencyOutOfRange = -2,
    TemperatureOutOfRange = -3,
    PressureOutOfBounds = -4,
    HumidityOutOfRange = -5
};

struct Environment {
    double temperature_c{20.0};
    double pressure_kpa{101.325};
    double humidity_pct{50.0};
};

struct AttenuationResult {
    double alpha_db_m{0.0};
    double alpha_db_km{0.0};
    double fr_oxygen_hz{0.0};
    double fr_nitrogen_hz{0.0};
    double molar_humidity{0.0};
    double alpha_classical{0.0};
    double alpha_oxygen{0.0};
    double alpha_nitrogen{0.0};
};

} // namespace acoustic
