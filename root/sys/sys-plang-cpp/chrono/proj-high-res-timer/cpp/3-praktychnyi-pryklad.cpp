// Функція запобігання оптимізаційному видаленню коду у C++
template <typename T>
void do_not_optimize(T&& value) {
    asm volatile("" : : "g"(value) : "memory");
}

int main() {
    constexpr size_t iterations = 1000;
    constexpr size_t vector_size = 500;

    BenchmarkRunner runner(iterations);

    std::vector<int> data(vector_size);

    for (size_t iter = 0; iter < iterations; ++iter) {
        // Заповнюємо вектор зворотно відпорядкованими даними
        std::iota(data.rbegin(), data.rend(), 1);

        {
            // Автоматичний RAII замір часу виконання блоку
            auto timer = runner.measure_scope();

            std::sort(data.begin(), data.end());
            do_not_optimize(data.data());
        }
    }

    runner.print_report("C++ std::sort");
    return 0;
}
