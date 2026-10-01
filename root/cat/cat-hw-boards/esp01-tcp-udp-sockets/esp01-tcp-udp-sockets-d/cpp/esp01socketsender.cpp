// Приклад класу керування передачею в сокет через AT+CIPSEND на C++
#include <iostream>
#include <string>
#include <vector>

class Esp01SocketSender {
public:
    static bool sendData(int socketId, const std::vector<uint8_t>& payload) {
        std::string cmd = "AT+CIPSEND=" + std::to_string(socketId) + "," + std::to_string(payload.size()) + "\r\n";
        
        // Передача командної стрічки
        std::cout << cmd;
        
        // Після очікування запрошення '>' надсилається корисний масив
        std::cout.write(reinterpret_cast<const char*>(payload.data()), payload.size());
        return true;
    }
};
