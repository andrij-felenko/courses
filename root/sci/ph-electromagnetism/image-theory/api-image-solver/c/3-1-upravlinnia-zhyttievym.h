/**
 * Створює новий екземпляр розв'язувача полів.
 * @param config Початкова конфігурація геометрії.
 * @return Вказівник на створений об'єкт es_solver_t.
 */
es_solver_t* es_solver_create(const es_solver_config_t* config);

/**
 * Звільняє всі ресурси, виділені під розв'язувач полів.
 * @param solver Вказівник на екземпляр розв'язувача.
 */
void es_solver_destroy(es_solver_t* solver);
