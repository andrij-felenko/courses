namespace std::execution {
    // Послідовне детерміноване виконання (C++17)
    class sequenced_policy { /* реалізаційно-визначено */ };
    inline constexpr sequenced_policy seq{};

    // Паралельне багатопотокове виконання (C++17)
    class parallel_policy { /* реалізаційно-визначено */ };
    inline constexpr parallel_policy par{};

    // Паралельне багатопотокове та векторизоване SIMD-виконання (C++17)
    class parallel_unsequenced_policy { /* реалізаційно-визначено */ };
    inline constexpr parallel_unsequenced_policy par_unseq{};

    // Однопотокове векторизоване SIMD-виконання (C++20)
    class unsequenced_policy { /* реалізаційно-визначено */ };
    inline constexpr unsequenced_policy unseq{};
}
