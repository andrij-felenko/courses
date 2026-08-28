// C++: подвійна перевірка на shared_mutex. Дешеве спільне читання під
// shared_lock; якщо промах — ексклюзивний unique_lock і друга перевірка під ним.
#include <shared_mutex>
#include <mutex>
#include <unordered_map>
#include <memory>
#include <string>

class LoggerRegistry {
    std::unordered_map<std::string, std::shared_ptr<Logger>> loggers_;
    std::shared_mutex mu_;
public:
    std::shared_ptr<Logger> get(const std::string& name) {
        {
            std::shared_lock read{mu_};            // читачі гарячого шляху не блокують одне одного
            auto it = loggers_.find(name);
            if (it != loggers_.end())
                return it->second;                 // швидкий шлях: ключ уже є
        }
        std::unique_lock write{mu_};               // на створення — ексклюзивний замок
        auto it = loggers_.find(name);             // друга перевірка: хтось міг створити, поки брали замок
        if (it != loggers_.end())
            return it->second;
        auto lg = std::make_shared<Logger>(name);
        loggers_.emplace(name, lg);
        return lg;
    }
};
