#include <stddef.h>
#include <stdbool.h>

// Властивості суцільного матеріалу
typedef struct {
    double conductivity;    // k: Коефіцієнт теплопровідності [Вт/(м·К)] (k > 0)
    double density;         // ρ: Густина матеріалу [кг/м³] (ρ > 0)
    double specific_heat;   // c_p: Питома теплоємність [Дж/(кг·К)] (c_p > 0)
    double emissivity;      // ε: Ступінь чорноти поверхні (0.0 <= ε <= 1.0)
} thermal_material_t;

// Параметри граничної умови для однієї грані
typedef struct {
    thermal_bc_type_t type; // Тип граничної умови (Dirichlet, Neumann, Robin, Radiation)
    double value;           // T_surface [°C] для 1-го роду або q_surface [Вт/м²] для 2-го роду
    double h_coeff;         // Коефіцієнт конвекції h [Вт/(м²·К)] (для Robin)
    double t_ambient;       // Температура довкілля T_amb [°C] (для Robin і Radiation)
} thermal_bc_t;

// Налаштування чисельної сітки та параметрів розв'язувача
typedef struct {
    size_t grid_x;          // Кількість вузлів сітки вздовж осі X
    size_t grid_y;          // Кількість вузлів сітки вздовж осі Y
    double dx;              // Просторовий крок дискретизації dx [м]
    double dy;              // Просторовий крок дискретизації dy [м]
    double dt;              // Часовий крок дискретизації dt [с]
    double max_time;        // Загальний фізичний час симуляції [с]
    double tolerance;       // Допуск сбіжності стаціонарного стану
    bool is_transient;      // прапорець: true = нестаціонарний, false = стаціонарний
} thermal_solver_config_t;
