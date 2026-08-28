#include <map>
#include <string>

class Config {
public:
    static Config& instance() {
        static Config inst;   // C++11: ініціалізується рівно раз, потокобезпечно
        return inst;
    }

    // єдиність без заборон нічого не варта: копію й присвоєння — під заборону
    Config(const Config&)            = delete;
    Config& operator=(const Config&) = delete;

    std::string get(const std::string& key) const {
        auto it = settings_.find(key);
        return it != settings_.end() ? it->second : std::string{};
    }

private:
    Config() { settings_ = load_from_disk(); }   // приватний, дорога робота
    std::map<std::string, std::string> settings_;
};

// вживання:  Config::instance().get("db.host");
