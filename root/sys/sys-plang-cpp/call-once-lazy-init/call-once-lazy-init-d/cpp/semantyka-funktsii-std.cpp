#include <mutex>
#include <memory>
#include <string>
#include <iostream>

struct DatabaseConfig {
    std::string connection_string;
    int timeout_ms = 3000;
};

class DatabaseService {
private:
    std::unique_ptr<DatabaseConfig> config_;
    mutable std::once_flag init_flag_;

    void initialize_config(const std::string& host, int port) {
        std::cout << "Завантаження конфігурації для " << host << ":" << port << "...\n";
        auto cfg = std::make_unique<DatabaseConfig>();
        cfg->connection_string = "host=" + host + ";port=" + std::to_string(port);
        cfg->timeout_ms = 5000;
        config_ = std::move(cfg);
    }

public:
    DatabaseService() = default;

    const DatabaseConfig& get_config() const {
        // Передаємо метод класу, вказівник this та аргументи конфігурації
        std::call_once(init_flag_, &DatabaseService::initialize_config, 
                       const_cast<DatabaseService*>(this), "db-primary.internal", 5432);
        return *config_;
    }
};
