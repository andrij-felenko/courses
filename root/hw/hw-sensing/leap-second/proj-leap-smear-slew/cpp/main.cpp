#include <iostream>
#include <chrono>
#include <cmath>
#include <numbers>
#include <memory>
#include <expected>
#include <string_view>
#include <thread>
#include <csignal>
#include <cstring>
#include <sys/timex.h>

namespace time_sync {

using namespace std::chrono_literals;

enum class SmearProfile {
    Linear,
    Cosine
};

// RAII-клас керування дисципліною годинника ядра
class ClockDiscipliner {
public:
    ClockDiscipliner() = default;
    
    // Деструктор гарантовано відновлює номінальну частоту при будь-якому виході
    ~ClockDiscipliner() {
        (void)restore_nominal_frequency();
    }

    // Заборона копіювання для збереження інваріанту єдиного керування генератором
    ClockDiscipliner(const ClockDiscipliner&) = delete;
    ClockDiscipliner& operator=(const ClockDiscipliner&) = delete;
    ClockDiscipliner(ClockDiscipliner&&) noexcept = default;
    ClockDiscipliner& operator=(ClockDiscipliner&&) noexcept = default;

    [[nodiscard]] std::expected<void, std::string_view> set_frequency_ppm(double ppm) const noexcept {
        struct timex tx{};
        tx.modes = ADJ_FREQUENCY;
        // Масштабування ppm у внутрішній 16-бітний дріб ядра Linux (1/65536 ppm)
        tx.freq = static_cast<long>(ppm * 65536.0);

        if (::adjtimex(&tx) < 0) {
            if (errno == EPERM) {
                return std::unexpected("Недостатньо привілеїв процесу (потрібен CAP_SYS_TIME)");
            }
            return std::unexpected("Системний збій виклику adjtimex");
        }
        return {};
    }

    [[nodiscard]] std::expected<void, std::string_view> restore_nominal_frequency() const noexcept {
        return set_frequency_ppm(0.0);
    }
};

// Обчислювач поправок розмазування
class LeapSmearEngine {
public:
    LeapSmearEngine(std::chrono::seconds window_duration, 
                    std::chrono::seconds leap_offset,
                    SmearProfile profile) noexcept
        : window_duration_{window_duration},
          leap_offset_{leap_offset},
          profile_{profile} {}

    [[nodiscard]] double calculate_offset_ppm(std::chrono::duration<double> elapsed) const noexcept {
        const double t = elapsed.count();
        const double total = static_cast<double>(window_duration_.count());
        const double delta = static_cast<double>(leap_offset_.count());

        if (t < 0.0 || t >= total) {
            return 0.0;
        }

        if (profile_ == SmearProfile::Linear) {
            // Постійне зміщення: - ΔΦ / T * 1e6
            return -(delta / total) * 1e6;
        } else {
            // Косинусний піднесений профіль: - (ΔΦ / T) * (1 - cos(2*pi*t / T)) * 1e6
            const double factor = 1.0 - std::cos(2.0 * std::numbers::pi * t / total);
            return -(delta / total) * factor * 1e6;
        }
    }

private:
    std::chrono::seconds window_duration_;
    std::chrono::seconds leap_offset_;
    SmearProfile profile_;
};

} // namespace time_sync

static volatile std::sig_atomic_t g_stop_signal = 0;

int main(int argc, char** argv) {
    std::signal(SIGINT, [](int) { g_stop_signal = 1; });
    std::signal(SIGTERM, [](int) { g_stop_signal = 1; });

    const auto profile = (argc > 1 && std::string_view(argv[1]) == "--linear")
                         ? time_sync::SmearProfile::Linear
                         : time_sync::SmearProfile::Cosine;

    std::cout << "=== Демон розмазування високосної секунди (Linux C++20) ===\n"
              << "Профіль: " << (profile == time_sync::SmearProfile::Cosine ? "Smooth Cosine" : "Linear") << "\n"
              << "Ініціалізація RAII-керування частотою ядра...\n";

    time_sync::ClockDiscipliner discipliner;
    time_sync::LeapSmearEngine engine(24h, 1s, profile);

    const auto start_time = std::chrono::steady_clock::now();
    const auto total_window = 24h;
    auto next_wakeup = start_time;

    while (!g_stop_signal) {
        const auto now = std::chrono::steady_clock::now();
        const std::chrono::duration<double> elapsed = now - start_time;

        if (elapsed >= total_window) {
            std::cout << "\nВікно розмазування успішно завершено.\n";
            break;
        }

        const double current_ppm = engine.calculate_offset_ppm(elapsed);
        auto result = discipliner.set_frequency_ppm(current_ppm);

        if (!result) {
            std::cerr << "\nПомилка: " << result.error() << "\n";
            return EXIT_FAILURE;
        }

        std::cout << "\rПрогрес: " << std::fixed << std::chrono::duration_cast<std::chrono::seconds>(elapsed).count()
                  << " с | Поправка: " << current_ppm << " ppm" << std::flush;

        next_wakeup += 500ms;
        std::this_thread::sleep_until(next_wakeup);
    }

    std::cout << "\nЗупинка демона. Автоматичне відновлення частоти через деструктор...\n";
    return EXIT_SUCCESS;
}
