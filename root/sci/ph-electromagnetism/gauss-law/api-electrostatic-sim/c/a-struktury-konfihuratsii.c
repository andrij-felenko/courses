// C API Grid Configuration & Boundary Conditions
typedef enum {
    BOUNDARY_DIRICHLET = 0, // Фіксований потенціал V = V_bound
    BOUNDARY_NEUMANN = 1,   // Фіксована нормальна похідна dV/dn = 0 (ізольована грань)
    BOUNDARY_ROBIN = 2      // Змішана гранична умова Robin
} boundary_type_t;

typedef struct {
    boundary_type_t type;
    double potential_volts; // Значення потенціалу для умов Діріхле
    double normal_derivative; // Значення нормальної похідної dV/dn
} boundary_condition_t;

typedef struct {
    size_t nx;              // Кількість вузлів по осі X
    size_t ny;              // Кількість вузлів по осі Y
    size_t nz;              // Кількість вузлів по осі Z
    double dx;              // Крок сітки по осі X (м)
    double dy;              // Крок сітки по осі Y (м)
    double dz;              // Крок сітки по осі Z (м)
    boundary_condition_t boundary_x_min;
    boundary_condition_t boundary_x_max;
    boundary_condition_t boundary_y_min;
    boundary_condition_t boundary_y_max;
    boundary_condition_t boundary_z_min;
    boundary_condition_t boundary_z_max;
} grid_config_t;
