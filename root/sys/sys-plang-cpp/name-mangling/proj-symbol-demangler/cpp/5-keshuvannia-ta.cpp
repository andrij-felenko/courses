#include <unordered_map>
#include <shared_mutex>
#include <string>
#include <string_view>
#include <mutex>

class SymbolCache {
public:
    std::string lookup_or_demangle(void* address, const char* mangled_name) {
        {
            // Швидке неблоковане читання з кешу
            std::shared_lock<std::shared_mutex> read_lock(mutex_);
            auto it = cache_.find(address);
            if (it != cache_.end()) {
                return it->second;
            }
        }

        // Якщо адреси немає в кеші — виконуємо деманґлінг
        std::string demangled = demangler_.demangle(mangled_name ? mangled_name : "");

        {
            // Ексклюзивний запис у кеш
            std::unique_lock<std::shared_mutex> write_lock(mutex_);
            cache_[address] = demangled;
        }

        return demangled;
    }

private:
    std::shared_mutex mutex_;
    std::unordered_map<void*, std::string> cache_;
    SymbolDemangler demangler_;
};
