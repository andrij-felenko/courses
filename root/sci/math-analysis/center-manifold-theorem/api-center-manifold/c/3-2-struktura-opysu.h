typedef struct {
    uint32_t dim_center;   /* Вимірність n центрального підпростору E^c */
    uint32_t dim_stable;   /* Вимірність m стійкого підпростору E^s */
    
    double  *matrix_A;     /* Двовимірний масив (n x n) нейтральної матриці A */
    double  *matrix_B;     /* Двовимірний масив (m x m) гурвіцевої матриці B */
    
    /* Функтор нелінійностей f(x, y) розміру n */
    void (*func_f)(const double *x, const double *y, double *out_f, void *user_data);
    
    /* Функтор нелінійностей g(x, y) розміру m */
    void (*func_g)(const double *x, const double *y, double *out_g, void *user_data);
    
    void *user_data;       /* Укористувацький контекст даних для функторів */
} cm_system_t;
