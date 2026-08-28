/**
 * Додає реальний точковий заряд до розв'язувача.
 */
es_status_t es_solver_add_charge(es_solver_t* solver, 
                                es_vec3_t position, 
                                double charge, 
                                uint32_t* out_id);

/**
 * Оновлює параметри геометрії граничних умов.
 */
es_status_t es_solver_update_config(es_solver_t* solver, const es_solver_config_t* config);
