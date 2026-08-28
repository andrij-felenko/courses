namespace std::linalg {
    // Загальний матрично-векторний добуток: y = A * x
    template <typename InMat, typename InVec, typename OutVec>
    void matrix_vector_product(InMat A, InVec x, OutVec y);

    // Симетричний добуток з урахуванням трикутника
    template <typename InMat, typename Triangle, typename InVec, typename OutVec>
    void symmetric_matrix_vector_product(InMat A, Triangle t, InVec x, OutVec y);

    // Розв'язання трикутної системи рівнянь: A * x = b
    template <typename InMat, typename Triangle, typename Diagonal, typename InOutVec>
    void triangular_matrix_vector_solve(InMat A, Triangle t, Diagonal d, InOutVec b);
}
