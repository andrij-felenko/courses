typedef struct {
    double real;   /* c_r: Фазова швидкість переміщення хвилі */
    double imag;   /* c_i: Інкремент зростання (c_i > 0 означає нестійкість!) */
} hydro_complex_t;

typedef struct {
    int num_modes;               /* Кількість знайдених власних мод (дорівнює N-4) */
    hydro_complex_t *eigenvalues;/* Динамічний масив комплексних власних значень [num_modes] */
    hydro_complex_t *eigenmodes; /* Динамічний масив власних векторів size: num_modes * N */
    int max_unstable_idx;        /* Індекс найнестійкішої моди з max(c_i) */
    double max_growth_rate;      /* Максимальний інкремент зростання γ_max = α * max(c_i) */
} hydro_spectrum_result_t;
