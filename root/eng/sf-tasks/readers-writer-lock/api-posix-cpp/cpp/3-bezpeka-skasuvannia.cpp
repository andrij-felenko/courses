#include <shared_mutex>
#include <string>
#include <string_view>

// У C++ завдяки семантиці RAII об'єкт std::shared_lock автоматично звільняє замок
// як при звичайному виході з області видимості, так і при розгортанні стека винятків (exception unwinding).
void safe_raii_read(std::shared_mutex& mutex, const std::string& shared_data, std::string& out_buf) {
    std::shared_lock<std::shared_mutex> lock(mutex);
    
    // Навіть якщо тут виникне виняток std::bad_alloc або std::runtime_error,
    // деструктор об'єкта lock гарантовано викличе unlock_shared().
    out_buf = shared_data;
}
