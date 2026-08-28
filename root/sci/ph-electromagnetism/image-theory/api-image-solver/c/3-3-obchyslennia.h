/**
 * Обчислює електричний потенціал V у заданій точці простору.
 */
es_status_t es_solver_eval_potential(const es_solver_t* solver, 
                                     es_vec3_t point, 
                                     double* out_potential);

/**
 * Обчислює вектор напруженості електричного поля E у заданій точці.
 */
es_status_t es_solver_eval_field(const es_solver_t* solver, 
                                es_vec3_t point, 
                                es_vec3_t* out_field_vector);

/**
 * Обчислює кулонівську силу, що діє на реальний заряд.
 */
es_status_t es_solver_eval_force(const es_solver_t* solver, 
                                uint32_t charge_id, 
                                es_vec3_t* out_force_vector);

/**
 * Обчислює густину індукованого поверхневого заряду sigma.
 */
es_status_t es_solver_eval_surface_density(const es_solver_t* solver,
                                            es_vec3_t boundary_point,
                                            double* out_sigma);
