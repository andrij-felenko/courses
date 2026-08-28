#include <iostream>
#include <vector>
#include <thread>
#include <latch>
#include <barrier>
#include <semaphore>
#include <span>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <memory>

// Константи моделювання
constexpr size_t GRID_HEIGHT = 256;
constexpr size_t GRID_WIDTH = 256;
constexpr int NUM_WORKERS = 4;
constexpr int NUM_ITERATIONS = 5;
constexpr ptrdiff_t MAX_LOG_SLOTS = 2;

// Спільний контекст просторової сітки
struct SimulationContext {
    std::vector<float> buffer_a;
    std::vector<float> buffer_b;
    std::vector<float>* current_in;
    std::vector<float>* current_out;

    float max_residual{0.0f};
    int current_step{0};

    SimulationContext()
        : buffer_a(GRID_HEIGHT * GRID_WIDTH, 20.0f),
          buffer_b(GRID_HEIGHT * GRID_WIDTH, 20.0f),
          current_in(&buffer_a),
          current_out(&buffer_b) {
        // Ініціалізація гарячої плями в центрі пластини (100 градусів)
        for (size_t y = GRID_HEIGHT / 4; y < 3 * GRID_HEIGHT / 4; ++y) {
            for (size_t x = GRID_WIDTH / 4; x < 3 * GRID_WIDTH / 4; ++x) {
                buffer_a[y * GRID_WIDTH + x] = 100.0f;
                buffer_b[y * GRID_WIDTH + x] = 100.0f;
            }
        }
    }
};

// Асинхронний дисковий логер із регулюванням навантаження через семафор
class AsyncLogger {
public:
    AsyncLogger() : slots_available_(MAX_LOG_SLOTS) {
        worker_ = std::jthread([this](std::stop_token st) {
            run_logger_loop(st);
        });
    }

    void submit_log_task(int step, float residual) {
        // Неблокуюча спроба захопити дозвіл із пулу слотів
        if (slots_available_.try_acquire()) {
            std::cout << "  -> [Logger] Заплановано збереження кадру " << step
                      << " (Макс. зміна температури = " << std::fixed << std::setprecision(4)
                      << residual << ")\n";
            // Симуляція відправки: звільняємо слот після завершення операції
            slots_available_.release();
        } else {
            std::cout << "  -> [Logger] Пул зайнятий, кадр " << step << " пропущено для уникнення затримки\n";
        }
    }

private:
    void run_logger_loop(std::stop_token st) {
        while (!st.stop_requested()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

    std::counting_semaphore<MAX_LOG_SLOTS> slots_available_;
    std::jthread worker_;
};

int main() {
    std::cout << "=== Запуск паралельного симулятора теплопровідності (C++20) ===\n";

    SimulationContext ctx;
    AsyncLogger logger;

    // 1. Latch: Одноразове зведення 4 потоків перед стартом
    std::latch start_rendezvous(NUM_WORKERS);

    // 2. Barrier Completion Callback: виконується строго один раз наприкінці кожної фази
    auto on_phase_complete = [&ctx, &logger]() noexcept {
        ++ctx.current_step;
        std::cout << "[Бар'єр] Фаза " << ctx.current_step << " успішно завершена.\n";

        // Асинхронний експорт кадру через обмежений семафор
        logger.submit_log_task(ctx.current_step, ctx.max_residual);

        // Безпечний обмін покажчиків вхідного та вихідного буферів
        std::swap(ctx.current_in, ctx.current_out);
        ctx.max_residual = 0.0f;
    };

    // Створюємо фазовий бар'єр C++20
    std::barrier phase_barrier(NUM_WORKERS, on_phase_complete);

    // Створюємо пул потоків-обчислювачів
    std::vector<std::jthread> workers;
    workers.reserve(NUM_WORKERS);

    const size_t rows_per_worker = (GRID_HEIGHT - 2) / NUM_WORKERS;

    for (int id = 0; id < NUM_WORKERS; ++id) {
        const size_t start_row = 1 + id * rows_per_worker;
        const size_t end_row = (id == NUM_WORKERS - 1) ? (GRID_HEIGHT - 1) : (start_row + rows_per_worker);

        workers.emplace_back([id, start_row, end_row, &ctx, &start_rendezvous, &phase_barrier]() {
            std::cout << "[Worker " << id << "] Ініціалізовано для рядків " << start_row << ".." << end_row - 1 << "\n";

            // [Фаза 1] Очікування повної готовності всіх потоків
            start_rendezvous.arrive_and_wait();

            // [Фаза 2] Ітераційний обчислювальний цикл
            for (int step = 0; step < NUM_ITERATIONS; ++step) {
                float local_max_delta = 0.0f;
                const auto& in_grid = *ctx.current_in;
                auto& out_grid = *ctx.current_out;

                // Обчислення 5-точкового скінченно-різницевого шаблону
                for (size_t y = start_row; y < end_row; ++y) {
                    for (size_t x = 1; x < GRID_WIDTH - 1; ++x) {
                        const size_t idx = y * GRID_WIDTH + x;
                        const float up = in_grid[(y - 1) * GRID_WIDTH + x];
                        const float down = in_grid[(y + 1) * GRID_WIDTH + x];
                        const float left = in_grid[y * GRID_WIDTH + (x - 1)];
                        const float right = in_grid[y * GRID_WIDTH + (x + 1)];

                        const float next_val = 0.25f * (up + down + left + right);
                        out_grid[idx] = next_val;

                        const float delta = std::fabs(next_val - in_grid[idx]);
                        if (delta > local_max_delta) {
                            local_max_delta = delta;
                        }
                    }
                }

                // Прибуття до бар'єра та очікування завершення фази
                phase_barrier.arrive_and_wait();
            }

            std::cout << "[Worker " << id << "] Завершив роботу.\n";
        });
    }

    // Очікування завершення всіх потоків через автоматичний RAII join у jthread
    for (auto& w : workers) {
        if (w.joinable()) {
            w.join();
        }
    }

    std::cout << "=== Обчислення завершено без блокувань, м'ютексів та гонок даних! ===\n";
    return 0;
}
