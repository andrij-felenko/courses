/* phase_embed.h — C-інтерфейс фазової реконструкції за теоремою Такена */
typedef struct {
    double delay_tau;   /* Часова затримка tau */
    size_t dim;         /* Розмірність вкладення d */
} PhaseEmbedConfig;

/**
 * @brief Оцінити оптимальну часову затримку tau за першим нулем автокореляції.
 * @param signal Вхідний часовий ряд.
 * @param length Довжина ряду.
 * @return Оптимальне значення tau у відліках.
 */
size_t phase_estimate_delay_tau(const double* signal, size_t length);

/**
 * @brief Реконструювати фазову траєкторію за допомогою вектора затримок.
 * @param signal Скалярний сигнал x(t).
 * @param length Кількість відліків.
 * @param config Параметри вкладення.
 * @param out_points [out] Реконструйований масив векторів Y(t).
 */
PhaseStatus phase_reconstruct_portrait(const double* signal, size_t length, const PhaseEmbedConfig* config, double* out_points);
