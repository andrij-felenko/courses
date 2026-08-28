// Фізичні константи
#define THERMAL_STEFAN_BOLTZMANN 5.670374419e-8 // Стала Стефана-Больцмана σ [Вт/(м²·К⁴)]
#define THERMAL_ABSOLUTE_ZERO_C  -273.15        // Абсолютний нуль [°C]

// Типи граничних умов
typedef enum {
    THERMAL_BC_DIRICHLET = 0, // 1-й рід: Задана фіксована температура T_surface [°C]
    THERMAL_BC_NEUMANN   = 1, // 2-й рід: Заданий тепловий потік q_surface [Вт/м²]
    THERMAL_BC_ROBIN     = 2, // 3-й рід: Конвекція h * (T_surface - T_ambient)
    THERMAL_BC_RADIATION = 3  // 4-й рід: Випромінювання ε * σ * (T_s⁴ - T_amb⁴)
} thermal_bc_type_t;

// Статуси виконання функцій розв'язувача
typedef enum {
    THERMAL_SUCCESS             =  0, // Обчислення завершено успішно
    THERMAL_ERROR_NULL_POINTER  = -1, // Передано нульовий вказівник на структуру
    THERMAL_ERROR_INVALID_PARAM = -2, // Передано некоректний фізичний параметр (k <= 0, dx <= 0)
    THERMAL_ERROR_CFL_VIOLATION = -3, // Часовий крок dt перевищує межу стійкості CFL
    THERMAL_ERROR_NO_CONVERGE   = -4  // Стаціонарний розв'язок не досяг допуску за max_iter
} thermal_status_t;
