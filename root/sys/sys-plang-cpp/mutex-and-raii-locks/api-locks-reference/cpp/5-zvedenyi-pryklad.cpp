#include <mutex>
#include <shared_mutex>
#include <iostream>

class SafeContainer {
private:
    mutable std::shared_mutex rw_mtx_;
    int data_ = 0;

public:
    // Читання: багато ниток одночасно через std::shared_lock
    int read_data() const {
        std::shared_lock<std::shared_mutex> lock(rw_mtx_);
        return data_;
    }

    // Запис: ексклюзивно через std::scoped_lock
    void write_data(int val) {
        std::scoped_lock lock(rw_mtx_);
        data_ = val;
    }
};
