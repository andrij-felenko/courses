// service.cpp
#include "logger.hpp"

class NetworkService {
public:
    NetworkService() {
        // Критична залежність: g_logger повинен бути готовим до роботи
        g_logger.log("NetworkService: налаштування сокетів та протоколів зв'язку");
    }
};

// Глобальний об'єкт мережевої служби
NetworkService g_network_service;
