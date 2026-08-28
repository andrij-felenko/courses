#include <mutex>

class Counter {
public:
    bool add(int delta) {
        // std::lock_guard захоплює замок у конструкторі
        // і автоматично звільняє його в деструкторі при будь-якому return чи винятку!
        std::lock_guard<std::mutex> guard(mutex_);
        
        if (delta < 0 && value_ < -delta) {
            return false; // Замок звільняється автоматично!
        }
        
        value_ += delta;
        return true;
    }

private:
    int value_{0};
    mutable std::mutex mutex_;
};
