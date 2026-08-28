typedef struct {
    size_t dim;                    /* Розмірність простору n */
    int64_t *b;                    /* Матриця базису b[i * n + j], розмір n x n */
    double *b_star;                /* Ортогональний базис Грама-Шмідта (n x n) */
    double *mu;                    /* Нижньотрикутна матриця коефіцієнтів mu (n x n) */
    double *b_star_sq;             /* Квадрати норм ||b_star[i]||^2 (розмір n) */
    double determinant;            /* Фундаментальний визначник det(L) */
    double log_determinant;        /* Натуральний логарифм визначника ln(det(L)) */
    double minkowski_radius;       /* Радіус Мінковського R_M = sqrt(n) * det(L)^(1/n) */
    double gaussian_heuristic;     /* Гауссова евристика GH(L) = sqrt(n/(2*pi*e)) * det(L)^(1/n) */
    double orthogonality_defect;   /* Дефект ортогональності prod(||b_i||) / det(L) */
    bool is_orthogonalized;        /* Прапорець готовності ортогонального розкладу */
} latgeom_basis_t;
