#include <atomic>
#include <thread>
#include <chrono>
#include <iostream>
#include <memory>

struct DataPayload {
    int id;
    int value;
};

class RcuSynchronizer {
private:
    std::atomic<DataPayload*> current_data_{nullptr};

public:
    explicit RcuSynchronizer(int initial_id, int initial_val) {
        current_data_.store(new DataPayload{initial_id, initial_val}, std::memory_order_relaxed);
    }

    ~RcuSynchronizer() {
        DataPayload* ptr = current_data_.load(std::memory_order_relaxed);
        delete ptr;
    }

    // Пасивний читач: нуль записів у пам'ять, відсутність затримок
    void execute_reader(int thread_id) const {
        // Завантаження вказівника із семантикою consume/acquire
        DataPayload* ptr = current_data_.load(std::memory_order_consume);
        if (ptr) {
            std::cout << "[Потік " << thread_id << "] Дані: " << ptr->value << std::endl;
        }
    }

    // Письменник: підміна та очікування grace period
    void update_payload(int new_id, int new_val) {
        DataPayload* old_ptr = current_data_.load(std::memory_order_relaxed);

        // 1. Копіювання та модифікація об'єкта
        DataPayload* new_ptr = new DataPayload{new_id, new_val};

        // 2. Атомарна підміна вказівника
        current_data_.store(new_ptr, std::memory_order_release);

        // 3. Очікування періоду відстрочки (Quiescent State для всіх читачів)
        wait_quiescent_states();

        // 4. Безумовно безпечне вивільнення застарілої пам'яті
        delete old_ptr;
    }

private:
    void wait_quiescent_states() {
        // У просторі користувача це перевірка проходження епох або бар'єрів читачів
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
};
