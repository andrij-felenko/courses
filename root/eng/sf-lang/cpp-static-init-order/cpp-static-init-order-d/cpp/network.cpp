// network.cpp
#include "logger.hpp"

class NetworkClient {
public:
    NetworkClient() {
        // Залежність: клієнт вимагає працездатного g_logger
        g_logger.log("NetworkClient: ініціалізація мережевих сокетів...");
    }
};

// Глобальний об'єкт мережевої підсистеми
NetworkClient g_network_client;
