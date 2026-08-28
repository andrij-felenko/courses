#if defined(__cpp_constexpr) && __cpp_constexpr >= 201907L
    // Алгоритм використовує динамічні контейнери на етапі компіляції (C++20)
    constexpr auto table = generate_lookup_vector();
#elif defined(__cpp_constexpr) && __cpp_constexpr >= 201304L
    // Спрощений алгоритм на базі статичного масиву C++14 з циклами
    constexpr auto table = generate_lookup_array();
#else
    // Звичайне runtime-обчислення для компіляторів C++11 та C++98
    const auto table = generate_lookup_array();
#endif
