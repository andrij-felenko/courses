class DataRepository {
public:
    // const-метод логічно не змінює клас, але модифікує м'ютекс під час lock_shared()
    std::string fetch_data() const {
        std::shared_lock<std::shared_mutex> lock(mutex_); // Успішно компілюється завдяки mutable!
        return cached_data_;
    }

private:
    mutable std::shared_mutex mutex_; // mutable дозволяє lock_shared() у const-методах
    std::string cached_data_;
};
