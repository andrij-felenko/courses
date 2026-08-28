struct Engine {
    template<typename T>
    void compute(T val);

    // ПОМИЛКА КОМПІЛЯЦІЇ: explicit specialization in non-namespace scope
    // template<>
    // void compute<int>(int val) {}
};

// ПРАВИЛЬНО: винесення повної спеціалізації на рівень namespace
template<>
inline void Engine::compute<int>(int val) {
    // Реалізація
}
