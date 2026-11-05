#include <mutex>
#include <vector>

class SafeDataBuffer {
private:
    mutable std::mutex mutex_;
    std::vector<int> buffer_;

public:
    void add_element(int raw_data) {
        // 1. Важкі обчислення поза критичною секцією
        int prepared_value = raw_data * 42 + 7;

        // 2. Використання RAII-обгортки для безпечного звуженого блокування
        {
            std::scoped_lock lock(mutex_);
            buffer_.push_back(prepared_value);
        } // Деструктор scoped_lock автоматично звільняє замок при виході з блоку

        // 3. Додаткова постобробка та сповіщення виконуються поза замком
    }
};
