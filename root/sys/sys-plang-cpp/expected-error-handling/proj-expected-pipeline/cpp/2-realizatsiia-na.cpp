// Ідіоматичний C++23 еквівалент з std::expected та RAII замість goto cleanup
#include <expected>
#include <string>
#include <string_view>
#include <fstream>
#include <sstream>

enum class ConfigStatus {
    Success = 0,
    FileNotFound,
    ReadFailed,
    InvalidPort,
    InvalidThreads,
    OutOfMemory
};

struct ServiceConfig {
    std::string db_host;
    int port{0};
    int worker_threads{0};
};

std::expected<std::string, ConfigStatus> read_config_file(std::string_view filepath) {
    std::ifstream file(std::string(filepath), std::ios::in | std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected(ConfigStatus::FileNotFound);
    }

    std::ostringstream ss;
    ss << file.rdbuf();
    if (file.bad()) {
        return std::unexpected(ConfigStatus::ReadFailed);
    }
    return ss.str();
}

std::expected<ServiceConfig, ConfigStatus> parse_and_validate(std::string_view buffer) {
    ServiceConfig cfg;
    std::string_view sv = buffer;
    
    auto p1 = sv.find(';');
    if (p1 == std::string_view::npos) return std::unexpected(ConfigStatus::InvalidPort);
    cfg.db_host = sv.substr(0, p1);
    
    auto rest = sv.substr(p1 + 1);
    auto p2 = rest.find(';');
    if (p2 == std::string_view::npos) return std::unexpected(ConfigStatus::InvalidPort);
    
    try {
        cfg.port = std::stoi(std::string(rest.substr(0, p2)));
        cfg.worker_threads = std::stoi(std::string(rest.substr(p2 + 1)));
    } catch (...) {
        return std::unexpected(ConfigStatus::InvalidPort);
    }

    if (cfg.port < 1 || cfg.port > 65535) return std::unexpected(ConfigStatus::InvalidPort);
    if (cfg.worker_threads < 1 || cfg.worker_threads > 128) return std::unexpected(ConfigStatus::InvalidThreads);

    return cfg;
}

std::expected<ServiceConfig, ConfigStatus> initialize_service_cpp(std::string_view config_path) {
    return read_config_file(config_path)
        .and_then(parse_and_validate); // RAII автоматично звільняє файловий дескриптор та буфери!
}
