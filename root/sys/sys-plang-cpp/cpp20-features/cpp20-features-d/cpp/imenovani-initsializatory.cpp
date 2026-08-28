struct ServerConfig {
    std::string host = "localhost";
    int port = 8080;
    int max_clients = 1000;
    bool enable_tls = false;
};

ServerConfig cfg{
    .port = 443,
    .max_clients = 5000,
    .enable_tls = true
}; // Поля мають слідувати у порядку їхнього оголошення в структурі
