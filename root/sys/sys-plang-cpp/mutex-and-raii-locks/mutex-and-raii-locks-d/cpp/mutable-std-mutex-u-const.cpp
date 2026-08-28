#include <mutex>
#include <string>

class ThreadSafeLogger {
    // mutable дозволяє змінювати стан mtx_ навіть усередині const-методів
    mutable std::mutex mtx_;
    std::string last_log_message_;

public:
    std::string get_last_message() const {
        std::lock_guard<std::mutex> lock(mtx_); // Зміна mutable поля mtx_ у const-методі!
        return last_log_message_;
    }
};
