#include <print>

int main() {
    std::string module = "CoreEngine";
    int thread_id = 4;
    double latency_ms = 0.428;

    // Вивід у стандартний stdout
    std::println("[{}] Потік {}: затримка {:.2f} мс", module, thread_id, latency_ms);

    // Прямий вивід у файл потоку C (FILE*)
    std::println(stderr, "Критична помилка ініціалізації");
}
