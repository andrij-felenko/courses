namespace std::linalg {
    // Масштабування вектора коефіцієнтом: v = alpha * v
    template <typename Alpha, typename InOutVec>
    void scale(Alpha alpha, InOutVec v);

    // Векторне додавання: y = x + y
    template <typename InVec, typename InOutVec>
    void add(InVec x, InOutVec y);

    // Обчислення скалярного добутку: sum(x_i * y_i) + init
    template <typename InVec1, typename InVec2, typename Scalar>
    Scalar dot(InVec1 x, InVec2 y, Scalar init);

    // Обчислення евклідової норми L2 вектора
    template <typename InVec, typename Scalar>
    Scalar vector_norm2(InVec x, Scalar init);

    // Пошук індексу елемента з максимальним абсолютним значенням
    template <typename InVec>
    size_t idx_abs_max(InVec x);
}
