#include <mutex>

class DataStructure {
    std::recursive_mutex r_mtx_;
    int value_ = 0;

public:
    void set_value(int v) {
        std::lock_guard<std::recursive_mutex> lock(r_mtx_);
        value_ = v;
    }

    void update_and_log(int v) {
        std::lock_guard<std::recursive_mutex> lock(r_mtx_);
        set_value(v); // Повторне захоплення того самого рекурсивного м'ютекса в тій самій нитці!
    }
};
