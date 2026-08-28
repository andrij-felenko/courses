template <typename T>
T clamp(T val, T min_val, T max_val) {
    if (val < min_val) return min_val;
    if (max_val < val) return max_val;
    return val;
}

// Виклики функції:
auto a = clamp(15, 0, 10);          // Неявне виведення: T = int
auto b = clamp<double>(15.5, 0, 10); // Явна типізація: T = double, аргументи 0 і 10 приводяться до double
