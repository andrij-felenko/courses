// network.cpp
#include "safe_logger.hpp"

class NetworkClient {
public:
    NetworkClient() {
        // Безпечно: instance() гарантує створення Logger до повернення посилання
        Logger::instance().log("NetworkClient: старт сокетів.");
    }
};

NetworkClient g_network_client;
