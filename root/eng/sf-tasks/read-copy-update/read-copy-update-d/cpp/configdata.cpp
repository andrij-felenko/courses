#include <shared_mutex>
#include <atomic>
#include <vector>
#include <memory>

// Класичний підхід із std::shared_mutex
struct ConfigData {
    std::vector<int> data;
};

class SharedConfigRW {
private:
    ConfigData data_;
    mutable std::shared_mutex lock_;

public:
    int read(size_t index) const {
        std::shared_lock<std::shared_mutex> guard(lock_); // Зміна лічильника читачів викликає кеш-інвалідацію
        return data_.data[index];
    }
};

// Концепція пасивного читача без блокувань
class SharedConfigPassive {
private:
    std::atomic<ConfigData*> data_ptr_{nullptr};

public:
    int read(size_t index) const {
        // Отримання вказівника без локауту та без зміни спільної пам'яті
        ConfigData* ptr = data_ptr_.load(std::memory_order_consume);
        return ptr->data[index];
    }
};
