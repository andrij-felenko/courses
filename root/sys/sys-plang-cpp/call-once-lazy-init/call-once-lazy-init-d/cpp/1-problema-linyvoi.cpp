#include <mutex>
#include <memory>
#include <string>

struct ConfigurationTable {
    std::string database_url;
    int max_pool_size = 100;
};

class ServiceGateway {
private:
    std::unique_ptr<ConfigurationTable> config_;
    mutable std::mutex config_mutex_;

    void load_configuration_from_network() {
        auto cfg = std::make_unique<ConfigurationTable>();
        cfg->database_url = "postgres://cluster.prod:5432/primary";
        cfg->max_pool_size = 256;
        config_ = std::move(cfg);
    }

public:
    const ConfigurationTable& get_configuration() const {
        std::lock_guard<std::mutex> lock(config_mutex_);
        if (!config_) {
            const_cast<ServiceGateway*>(this)->load_configuration_from_network();
        }
        return *config_;
    }
};
