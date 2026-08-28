/* ІСТОРИЧНО ЗЛАМАНА РЕАЛІЗАЦІЯ DOUBLE-CHECKED LOCKING (C++03) */
class BrokenSingleton {
public:
    static BrokenSingleton* get_instance() {
        if (instance_ == nullptr) { // Перша перевірка (без замка)
            std::lock_guard<std::mutex> lock(mutex_);
            if (instance_ == nullptr) { // Друга перевірка (під замком)
                instance_ = new BrokenSingleton(); // НЕБЕЗПЕКА!
            }
        }
        return instance_;
    }
private:
    static BrokenSingleton* instance_;
    static std::mutex mutex_;
};
