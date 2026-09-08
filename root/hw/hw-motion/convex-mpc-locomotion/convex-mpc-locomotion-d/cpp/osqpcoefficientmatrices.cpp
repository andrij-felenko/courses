struct OSQPCoefficientMatrices {
    // Вектор градієнта лінійної частини g^T * U
    std::vector<c_float> q_grad;
    
    // Розріджена матриця Гессе H (лише верхній трикутник)
    std::vector<c_float> H_values;
    std::vector<c_int>   H_inner_indices;
    std::vector<c_int>   H_outer_index_pointers;
    
    // Розріджена матриця обмежень A_ineq
    std::vector<c_float> A_values;
    std::vector<c_int>   A_inner_indices;
    std::vector<c_int>   A_outer_index_pointers;
    
    // Вектори нижніх та верхніх меж l <= A*u <= u
    std::vector<c_float> lower_bounds;
    std::vector<c_float> upper_bounds;
    
    void updateStanceMask(const std::array<bool, 4>& stance_legs, int step) {
        // Оновлення меж сили f_z для опорних та махових ніг
        for (int leg = 0; leg < 4; ++leg) {
            int idx = step * 12 + leg * 3 + 2;
            if (stance_legs[leg]) {
                lower_bounds[idx] = 10.0;     // f_min = 10 Н
                upper_bounds[idx] = 400.0;    // f_max = 400 Н
            } else {
                lower_bounds[idx] = 0.0;      // Махова лапа: f = 0
                upper_bounds[idx] = 0.0;
            }
        }
    }
};
