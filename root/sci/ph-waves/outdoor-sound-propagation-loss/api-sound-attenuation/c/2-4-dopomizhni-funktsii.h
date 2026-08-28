/**
 * @brief Обчислює молярну концентрацію водяної пари h (%).
 */
double iso9613_calculate_molar_humidity(double temp_c, double pressure_kpa, double humidity_pct);

/**
 * @brief Обчислює частоту релаксації кисню f_r,O (Гц).
 */
double iso9613_calculate_fr_oxygen(double temp_c, double pressure_kpa, double humidity_pct);

/**
 * @brief Обчислює частоту релаксації азоту f_r,N (Гц).
 */
double iso9613_calculate_fr_nitrogen(double temp_c, double pressure_kpa, double humidity_pct);
