#include <iostream>
#include <memory>
#include <atomic>
#include <stdexcept>

// Спеціалізований виняток скасування для асинхронного стека
class cancellation_exception : public std::runtime_error {
public:
    cancellation_exception() 
        : std::runtime_error("Операцію скасовано за запитом токена") {}
};

// Маркер скасування для перевірки точок скасування
class cancellation_token {
private:
    std::shared_ptr<std::atomic<bool>> flag_;
public:
    explicit cancellation_token(std::shared_ptr<std::atomic<bool>> flag) 
        : flag_(std::move(flag)) {}

    [[nodiscard]] bool is_cancellation_requested() const noexcept {
        return flag_ && flag_->load(std::memory_order_acquire);
    }

    void throw_if_cancellation_requested() const {
        if (is_cancellation_requested()) {
            throw cancellation_exception();
        }
    }
};

// Низькорівнева підзадача (checkpoint)
int compute_subtask(int step, const cancellation_token& token) {
    // Точка скасування перевіряє стан токена
    token.throw_if_cancellation_requested();

    if (step < 0) {
        throw std::invalid_argument("Некоректне значення кроку"); // Доменна помилка
    }

    return step * 42;
}

// Високорівнева задача ланцюжка
int execute_pipeline(int steps, const cancellation_token& token) {
    int total_result = 0;
    for (int i = 0; i < steps; ++i) {
        // Перевірка перед початком ітерації
        token.throw_if_cancellation_requested();

        try {
            total_result += compute_subtask(i, token);
        } catch (const cancellation_exception&) {
            // Сигнал скасування НЕ маскується, а прокидається вище
            throw;
        } catch (const std::exception& ex) {
            // Обробка або трансляція звичайної помилки виконання
            std::cerr << "Помилка виконання підзадачі: " << ex.what() << std::endl;
            throw;
        }
    }
    return total_result;
}
