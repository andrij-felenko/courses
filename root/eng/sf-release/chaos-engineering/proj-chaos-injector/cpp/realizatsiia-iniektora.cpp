#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include <random>
#include <string>
#include <string_view>
#include <format>
#include <memory>
#include <system_error>
#include <cstdint>
#include <sys/timerfd.h>
#include <unistd.h>

enum class ChaosState : uint8_t {
    Idle = 0,
    Running,
    Aborted,
    Completed
};

struct ChaosConfig {
    std::chrono::seconds duration{4};
    std::chrono::milliseconds delay{120};
    uint32_t failure_rate_pct{35};
    double max_allowed_err_pct{30.0};
};

/* RAII-обгортка над системним дескриптором timerfd */
class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

class ChaosCoordinator {
public:
    explicit ChaosCoordinator(ChaosConfig config)
        : config_(config), state_(ChaosState::Idle) {}

    void run() {
        state_.store(ChaosState::Running, std::memory_order_release);
        std::cout << "=== Запуск системного координатора хаос-експериментів (Modern C++) ===\n";

        UniqueFd timer_fd = create_watchdog_timer(config_.duration);

        // Запуск потоків моніторингу та воркера з використанням std::jthread
        std::jthread monitor_thread([this, fd = timer_fd.get()](std::stop_token stoken) {
            monitor_loop(stoken, fd);
        });

        std::jthread worker_thread([this](std::stop_token stoken) {
            worker_loop(stoken);
        });

        // Головний потік чекає завершення (коли state перейде з Running)
        while (state_.load(std::memory_order_acquire) == ChaosState::Running) {
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        // Надсилаємо запит на зупинку jthread
        monitor_thread.request_stop();
        worker_thread.request_stop();
        // RAII jthread автоматично викличе join() при виході зі скоупу

        print_summary();
    }

private:
    static UniqueFd create_watchdog_timer(std::chrono::seconds duration) {
        int fd = ::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "timerfd_create failed");
        }
        struct itimerspec its{};
        its.it_value.tv_sec = duration.count();
        if (::timerfd_settime(fd, 0, &its, nullptr) < 0) {
            ::close(fd);
            throw std::system_error(errno, std::generic_category(), "timerfd_settime failed");
        }
        return UniqueFd(fd);
    }

    void rollback(std::string_view reason) {
        ChaosState expected = ChaosState::Running;
        if (state_.compare_exchange_strong(expected, ChaosState::Aborted, std::memory_order_acq_rel)) {
            std::cout << std::format("\n[ROLLBACK] Аварійна зупинка хаос-ін'єкції! Причина: {}\n", reason);
            std::cout << "[ROLLBACK] Відновлення мережевих маршрутів та правил ядра...\n";
            std::cout << "[ROLLBACK] Базовий стан відновлено (Clean State).\n";
        }
    }

    void monitor_loop(std::stop_token stoken, int timer_fd) {
        uint64_t exp_buf = 0;
        while (!stoken.stop_requested() && state_.load(std::memory_order_acquire) == ChaosState::Running) {
            // Перевірка спрацювання сторожового таймера ядра
            ssize_t s = ::read(timer_fd, &exp_buf, sizeof(exp_buf));
            if (s == sizeof(exp_buf)) {
                rollback("Вичерпано ліміт часу експерименту (Watchdog TTL)");
                break;
            }

            // Перевірка порушення SLI
            uint64_t total = total_requests_.load(std::memory_order_relaxed);
            uint64_t failed = failed_requests_.load(std::memory_order_relaxed);
            if (total > 20) {
                double current_err_pct = (static_cast<double>(failed) / static_cast<double>(total)) * 100.0;
                if (current_err_pct > config_.max_allowed_err_pct) {
                    rollback(std::format("Порушення SLO! Помилки: {:.2f}% (ліміт: {:.2f}%)",
                                         current_err_pct, config_.max_allowed_err_pct));
                    break;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

    void worker_loop(std::stop_token stoken) {
        std::mt19937_64 rng(std::random_device{}());
        std::uniform_int_distribution<uint32_t> dist(0, 99);

        while (!stoken.stop_requested() && state_.load(std::memory_order_acquire) == ChaosState::Running) {
            total_requests_.fetch_add(1, std::memory_order_relaxed);
            uint32_t roll = dist(rng);

            if (roll < config_.failure_rate_pct) {
                std::this_thread::sleep_for(config_.delay);
                failed_requests_.fetch_add(1, std::memory_order_relaxed);
                std::cout << std::format("[WORKER] Ін'єкція: затримка {}ms -> Відмова 503\n", config_.delay.count());
            } else {
                std::this_thread::sleep_for(std::chrono::milliseconds(15));
                std::cout << "[WORKER] Запит оброблено успішно (200 OK)\n";
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    }

    void print_summary() const {
        ChaosState final_st = state_.load(std::memory_order_acquire);
        if (final_st == ChaosState::Running) {
            std::cout << "\n[SUCCESS] Хаос-експеримент завершено успішно без порушень SLO.\n";
        }
        uint64_t total = total_requests_.load(std::memory_order_relaxed);
        uint64_t failed = failed_requests_.load(std::memory_order_relaxed);
        double err_pct = total ? (static_cast<double>(failed) / static_cast<double>(total)) * 100.0 : 0.0;
        std::cout << std::format("Підсумок: {} запитів, {} помилок ({:.2f}%)\n", total, failed, err_pct);
    }

    ChaosConfig config_;
    std::atomic<ChaosState> state_{ChaosState::Idle};
    std::atomic<uint64_t> total_requests_{0};
    std::atomic<uint64_t> failed_requests_{0};
};

int main() {
    try {
        ChaosConfig config{
            .duration = std::chrono::seconds(4),
            .delay = std::chrono::milliseconds(120),
            .failure_rate_pct = 35,
            .max_allowed_err_pct = 30.0
        };

        ChaosCoordinator coordinator(config);
        coordinator.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка координатора: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
