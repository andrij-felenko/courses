/**
 * @brief Обчислює потенціал та поле точкового диполя.
 * @param dipole Вказівник на структуру точкового диполя.
 * @param obs_point Координати точки спостереження [м].
 * @param min_r_cutoff Мінімальний радіус зрізу для запобігання сингулярності [м].
 * @param result Вказівник на структуру для запису результату.
 * @return Код помилки (0 — успіх, -1 — null pointer, 1 — точка в зоні сингулярності).
 */
int dipole_calc_field(const electric_dipole_t* dipole,
                      const dipole_vec3_t* obs_point,
                      double min_r_cutoff,
                      dipole_field_result_t* result);
