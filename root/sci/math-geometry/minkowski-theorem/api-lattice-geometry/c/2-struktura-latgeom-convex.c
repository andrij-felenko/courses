typedef enum {
    LATGEOM_BODY_ELLIPSOID = 1,    /* Еліпсоїд: x^T * Q * x <= r^2 */
    LATGEOM_BODY_HYPERCUBE = 2,    /* Симетричний паралелепіпед: |l_i(x)| <= c_i */
    LATGEOM_BODY_CROSS_POLYTOPE = 3/* Крос-політоп: sum |l_i(x)| <= r */
} latgeom_body_type_t;

typedef struct {
    size_t dim;                    /* Розмірність простору n */
    latgeom_body_type_t type;      /* Геометричний тип тіла */
    double *shape_matrix;          /* Матриця форми Q розміру n x n (симетрична додатно визначена) */
    double *limits;                /* Межі координат c_i (розмір n) */
    double radius;                 /* Евклідів радіус r (для кулі або еліпсоїда) */
    double volume;                 /* Аналітично обчислений n-вимірний об'єм vol(K) */
} latgeom_convex_body_t;
