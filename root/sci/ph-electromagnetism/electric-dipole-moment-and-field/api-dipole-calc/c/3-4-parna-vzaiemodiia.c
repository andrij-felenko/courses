/**
 * @brief Обчислює енергію взаємодії двох диполів U_12.
 * @param d1 Вказівник на перший диполь.
 * @param d2 Вказівник на другий диполь.
 * @param relative_permittivity Відносна діелектрична проникність середовища eps_r.
 * @param energy Вказівник на змінну для запису енергії [Дж].
 * @return Код помилки (0 — успіх, -1 — null pointer, 1 — збіг координат диполів).
 */
int dipole_calc_interaction_energy(const electric_dipole_t* d1,
                                    const electric_dipole_t* d2,
                                    double relative_permittivity,
                                    double* energy);
