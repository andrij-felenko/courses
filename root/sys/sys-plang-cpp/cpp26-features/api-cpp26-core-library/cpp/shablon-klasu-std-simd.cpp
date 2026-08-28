namespace std {
    namespace simd_abi {
        using scalar = /* скалярна емуляція */;
        template <size_t N> using fixed_size = /* фіксована ширина смуги */;
        template <typename T> using native = /* максимальний доступний апаратний регістр */;
        template <typename T> using compatible = /* переносимий ABI-вектор */;
    }

    template <typename T, typename Abi = simd_abi::native<T>>
    class simd {
    public:
        using value_type = T;
        using abi_type = Abi;
        using mask_type = simd_mask<T, Abi>;

        static constexpr size_t size() noexcept;

        simd() noexcept = default;
        simd(T broadcast_value) noexcept;

        // Завантаження та вивантаження у фізичну пам'ять
        void copy_from(const T* mem, element_aligned_tag) noexcept;
        void copy_to(T* mem, element_aligned_tag) const noexcept;

        // Покомпонентний доступ до смуг регістра
        T operator[](size_t index) const noexcept;

        // Поелементна векторна арифметика
        simd& operator+=(const simd&) noexcept;
        simd& operator*=(const simd&) noexcept;
        simd operator-() const noexcept;
    };
}
