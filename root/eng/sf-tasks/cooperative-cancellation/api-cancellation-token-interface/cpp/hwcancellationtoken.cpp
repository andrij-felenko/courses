#include <iostream>
#include <atomic>
#include <memory>
#include <thread>
#include <chrono>

// Токен скасування з низькорівневою атомарною синхронізацією
class HwCancellationToken {
public:
    explicit HwCancellationToken(std::shared_ptr<std::atomic<bool>> flag)
        : flag_(std::move(flag)) {}

    [[nodiscard]] bool is_cancellation_requested() const noexcept {
        return flag_ && flag_->load(std::memory_order_acquire);
    }

private:
    std::shared_ptr<std::atomic<bool>> flag_;
};

// Джерело ініціації скасування
class HwCancellationTokenSource {
public:
    HwCancellationTokenSource()
        : flag_(std::make_shared<std::atomic<bool>>(false)) {}

    HwCancellationToken get_token() const noexcept {
        return HwCancellationToken(flag_);
    }

    void cancel() noexcept {
        if (flag_) {
            flag_->store(true, std::memory_order_release);
        }
    }

private:
    std::shared_ptr<std::atomic<bool>> flag_;
};

// RAII-обгортка для апаратного периферійного модуля
class HardwareRegisterGuard {
public:
    explicit HardwareRegisterGuard(uint32_t channel)
        : channel_(channel), active_(true) {
        std::cout << "[RAII] Апаратний канал DMA " << channel_ << " ініціалізовано.\n";
    }

    ~HardwareRegisterGuard() {
        if (active_) {
            stop_hardware();
        }
    }

    void stop_hardware() noexcept {
        if (active_) {
            std::cout << "[RAII] Апаратне вимкнення та очищення регістрів каналу " << channel_ << ".\n";
            active_ = false;
        }
    }

    HardwareRegisterGuard(const HardwareRegisterGuard&) = delete;
    HardwareRegisterGuard& operator=(const HardwareRegisterGuard&) = delete;

private:
    uint32_t channel_;
    bool active_;
};

// Задача низькорівневої обробки
void process_hardware_stream(HwCancellationToken token) {
    HardwareRegisterGuard hw_guard(2); // Автоматичний деструктор очистить регістри

    for (int step = 0; step < 30; ++step) {
        if (token.is_cancellation_requested()) {
            std::cout << "[Worker] Контрольна точка: отримано запит зупинки!\n";
            // RAII автоматично викличе stop_hardware() при виході з функції
            return;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    std::cout << "[Worker] Обробку стриму повністю завершено.\n";
}
