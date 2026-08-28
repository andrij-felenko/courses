/**
 * @brief Обчислює енергію, момент і силу, що діють на диполь.
 * @param dipole Вказівник на структуру диполя.
 * @param E_ext Вектор напруженості зовнішнього поля E у точці диполя [В/м].
 * @param grad_E_x Градієнт dE/dx (вектор трьох похідних dEx/dx, dEy/dx, dEz/dx).
 * @param grad_E_y Градієнт dE/dy.
 * @param grad_E_z Градієнт dE/dz.
 * @param result Вказівник на структуру результату динаміки.
 * @return Код помилки (0 — успіх, -1 — null pointer).
 */
int dipole_calc_dynamics(const electric_dipole_t* dipole,
                         const dipole_vec3_t* E_ext,
                         const dipole_vec3_t* grad_E_x,
                         const dipole_vec3_t* grad_E_y,
                         const dipole_vec3_t* grad_E_z,
                         dipole_dynamics_t* result);
