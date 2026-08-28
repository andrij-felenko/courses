/**
 * @brief Обчислює підсумковий рівень звукового тиску SPL на відстані r з урахуванням розходження та поглинання.
 * 
 * @param[in] spl_ref_db  Початковий рівень SPL на опорній відстані r_ref, дБ.
 * @param[in] r_ref_m     Опорна відстань від джерела (наприклад, 1.0 м або 10.0 м).
 * @param[in] r_target_m  Цільова відстань від джерела, м.
 * @param[in] alpha_db_m  Коефіцієнт загасання середовища, дБ/м.
 * @return double Підсумковий рівень SPL у дБ на відстані r_target_m.
 */
double iso9613_calculate_total_spl(
    double spl_ref_db,
    double r_ref_m,
    double r_target_m,
    double alpha_db_m
);
