// Використання хронометра у C
int main(void) {
    const size_t iterations = 1000;
    const size_t array_size = 500;

    benchmark_stats_t stats;
    if (benchmark_stats_init(&stats, iterations) != 0) {
        fprintf(stderr, "Помилка виділення пам'яті під заміри.\n");
        return 1;
    }

    int* data = (int*)malloc(array_size * sizeof(int));

    for (size_t iter = 0; iter < iterations; ++iter) {
        // Ініціалізація тестового масиву
        for (size_t i = 0; i < array_size; ++i) {
            data[i] = (int)(array_size - i);
        }

        uint64_t start_ns = get_monotonic_ns();

        // Тестове обчислення: бульбашкове сортування
        for (size_t i = 0; i < array_size - 1; ++i) {
            for (size_t j = 0; j < array_size - i - 1; ++j) {
                if (data[j] > data[j + 1]) {
                    int tmp = data[j];
                    data[j] = data[j + 1];
                    data[j + 1] = tmp;
                }
            }
        }

        // Бар'єр пам'яті для компілятора: гарантує завершення дій до зчитування часу
        __asm__ __volatile__("" : : "g"(data) : "memory");

        uint64_t end_ns = get_monotonic_ns();
        benchmark_stats_add(&stats, end_ns - start_ns);
    }

    benchmark_stats_print_report(&stats, "C BubbleSort");
    
    free(data);
    benchmark_stats_free(&stats);
    return 0;
}
