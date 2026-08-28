// Концептуальна схема організації вектора в GNU libstdc++
template <typename Tp, typename Alloc>
struct _Vector_base {
    struct _Vector_impl_data {
        Tp* _M_start{nullptr};
        Tp* _M_finish{nullptr};
        Tp* _M_end_of_storage{nullptr};
    };

    // Оптимізація: спадкування від алокатора Tp_alloc_type через EBO
    struct _Vector_impl : public Alloc, public _Vector_impl_data {
        _Vector_impl() = default;
        explicit _Vector_impl(const Alloc& a) : Alloc(a) {}
    };

    _Vector_impl _M_impl;
};
