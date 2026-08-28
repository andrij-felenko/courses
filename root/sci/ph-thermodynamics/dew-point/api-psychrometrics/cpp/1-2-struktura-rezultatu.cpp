namespace physics::thermal {

struct PsychroResult {
    double air_temp_c;          // Вхідна температура повітря, °C
    double rel_humidity_pct;    // Вхідна відносна вологість, %
    double dew_point_c;         // Обчислена температура точки роси, °C
    double frost_point_c;       // Обчислена температура точки інею, °C
    double sat_vapor_press_kpa; // Тиск насиченої водяної пари, кПа
    double vapor_press_kpa;     // Поточний парціальний тиск водяної пари, кПа
};

} // namespace physics::thermal
