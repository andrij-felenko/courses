#include <mutex>

// Використання розширень безпеки Clang
class SafeStorage {
public:
    void update(int val) {
        std::lock_guard<std::mutex> lock(mutex_);
        data_ = val; // Компілятор перевіряє, що mutex_ захоплено!
    }

    int get() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return data_;
    }

private:
    mutable std::mutex mutex_;
    int data_{0}; // Прив'язка даних до замка на рівні типів
};
