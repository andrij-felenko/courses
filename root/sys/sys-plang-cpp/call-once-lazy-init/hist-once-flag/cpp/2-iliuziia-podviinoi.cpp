// Наївний патерн DCLP на C++98/03 (історичний небезпечний антипатерн)
#include <mutex>
#include <memory>

struct MatrixFilter {
    int coefficients[256];
    MatrixFilter() { coefficients[0] = 100; }
};

MatrixFilter* g_filter = nullptr;
std::mutex g_filter_mtx;

MatrixFilter* get_matrix_filter_broken() {
    if (g_filter == nullptr) { // Перша перевірка без блокування
        std::lock_guard<std::mutex> lock(g_filter_mtx);
        if (g_filter == nullptr) { // Друга перевірка під замком
            // Рядок нижче розпадається компілятором на 3 кроки:
            // Крок 1: operator new(sizeof(MatrixFilter)) — виділення пам'яті
            // Крок 2: MatrixFilter::MatrixFilter() — виконання конструктора
            // Крок 3: присвоєння адреси змінній g_filter
            g_filter = new MatrixFilter();
        }
    }
    return g_filter;
}
