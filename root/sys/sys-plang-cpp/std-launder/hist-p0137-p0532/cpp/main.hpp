struct ServerConfig {
    const int port;
    const std::string host;
};

std::optional<ServerConfig> opt;
opt.emplace(ServerConfig{8080, "localhost"});

// Перезапис значення новою конфігурацією:
opt.emplace(ServerConfig{9090, "127.0.0.1"});
