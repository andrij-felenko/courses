#include <mutex>
#include <shared_mutex>
#include <iostream>

template<bool ThreadSafe = true>
class ThreadSafeMetricsRegistry {
public:
    void increment(const std::string& name) {
        if constexpr (ThreadSafe) {
            // Захоплюємо ексклюзивне блокування тільки якщо увімкнено багатопотоковість
            std::unique_lock lock(mutex_);
            unsafe_increment(name);
        } else {
            // Прямий виклик без жодних атомарних операцій та захоплення блокувань
            unsafe_increment(name);
        }
    }

private:
    void unsafe_increment(const std::string& name) {
        // Інкремент внутрішнього лічильника метрик
        std::cout << "Оновлено метрику: " << name << "\n";
    }

    // Для однопотокового варіанта м'ютекс взагалі можна вилучити або зробити порожнім
    std::mutex mutex_;
};
