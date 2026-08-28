typedef bool (*ah_oracle_callback_t)(uint64_t query_id, void* user_ctx);

/**
 * @brief Симуляція оцінки належності елемента до предикату рівня jump_level.
 * 
 * @param element Вхідний елемент для перевірки.
 * @param jump_level Індекс необхідного оракульного стрибка (0 для ∅, 1 для K, 2 для K').
 * @param oracle Зворотний виклик для звернення до оракула нижчого рівня.
 * @param user_ctx Довільний контекст користувача, що передається в oracle.
 * @param out_result Вказівник на результат перевірки (true/false).
 * @return int AH_SUCCESS у разі завершення обчислення; код помилки при нерозв'язності або циклюванні.
 */
int ah_oracle_evaluate(uint64_t element, 
                       uint32_t jump_level, 
                       ah_oracle_callback_t oracle, 
                       void* user_ctx, 
                       bool* out_result);
