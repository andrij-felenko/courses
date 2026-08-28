#ifdef __cplusplus
extern "C" {
#endif

// Обчислити температуропровідність α = k / (ρ * c_p) [м²/с]
double thermal_calc_diffusivity(const thermal_material_t* mat);

// Обчислити максимально припустимий часовий крок dt_max [с] за умовою CFL:
// dt_max = 0.5 * min(dx², dy²) / α
double thermal_get_max_stable_dt(const thermal_material_t* mat, double dx, double dy);

// Обчислити конвективний тепловий потік за законом Ньютона: q = h * (T_s - T_amb)
double thermal_calc_convective_flux(double h_coeff, double t_surface, double t_ambient);

// Обчислити радіаційний тепловий потік за законом Стефана-Больцмана:
// q = ε * σ * ((T_s + 273.15)⁴ - (T_amb + 273.15)⁴)
double thermal_calc_radiative_flux(double emissivity, double t_surface, double t_ambient);

// Запустити двовимірний розв'язувач рівняння теплопровідності
thermal_status_t thermal_solve_2d(
    const thermal_solver_config_t* config,
    const thermal_material_t* material,
    const thermal_bc_t boundary_conditions[4], // Граничні умови: [Північ, Південь, Схід, Захід]
    double* grid_output                          // Вихідний масив розміром grid_x * grid_y
);

#ifdef __cplusplus
}
#endif
