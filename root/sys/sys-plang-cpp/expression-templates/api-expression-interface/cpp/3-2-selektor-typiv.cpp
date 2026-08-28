template <typename T>
struct expression_storage_traits {
    // Якщо T є lvalue-посиланням (наприклад, Vector&), зберігаємо const Vector&.
    // Якщо T є значенням (тимчасовим rvalue, наприклад Vector), зберігаємо за значенням Vector.
    using type = std::conditional_t<
        std::is_lvalue_reference_v<T>,
        const std::remove_reference_t<T>&,
        const std::remove_reference_t<T>
    >;
};

template <typename T>
using storage_type_t = typename expression_storage_traits<T>::type;
