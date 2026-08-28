# 1. Компіляція бенчмарка з налагоджувальними символами та повною оптимізацією
clang -O3 -march=native -flto -g -fno-omit-frame-pointer benchmark.c -o benchmark_metrics -lm

# 2. Збір базової статистики лічильників продуктивності PMU
perf stat -e cycles,instructions,cache-misses,branch-misses,L1-dcache-load-misses ./benchmark_metrics

# 3. Запис детального профілю з відстеженням стека викликів
perf record -F 999 -g ./benchmark_metrics

# 4. Перегляд інтерактивного звіту з асемблерним аннотуванням гарячих циклів
perf report --stdio
