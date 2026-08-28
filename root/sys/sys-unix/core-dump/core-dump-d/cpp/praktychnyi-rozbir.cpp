#include <iostream>

struct DatabaseConfig {
    std::string host;
    uint16_t port;
};

void connect_to_database(DatabaseConfig* config) {
    // Якщо config дорівнює nullptr, спроба прочитати config->host викликає SIGSEGV
    std::cout << "Connecting to host: " << config->host << std::endl;
}

int main() {
    DatabaseConfig* cfg = nullptr;
    connect_to_database(cfg);
    return 0;
}
