// Приклад використання std::stop_token та std::stop_callback для розблокування мережевого сокета в C++
#include <iostream>
#include <thread>
#include <stop_token>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

class BlockingSocketReader {
private:
    int sockfd_;

public:
    explicit BlockingSocketReader(int sockfd) : sockfd_(sockfd) {}

    ssize_t read_data(char* buffer, size_t length, std::stop_token stoken) {
        if (stoken.stop_requested()) {
            return -1; // Скасування запитано до початку операції
        }

        // Реєструємо зворотний виклик stop_callback
        // При отриманні сигналу скасування спрацює shutdown(), що розблокує read()
        std::stop_callback callback(stoken, [this]() {
            ::shutdown(sockfd_, SHUT_RDWR);
        });

        ssize_t bytes_read = ::read(sockfd_, buffer, length);
        if (stoken.stop_requested()) {
            return -1; // Скасування відбулося під час блокуючого виклику
        }

        return bytes_read;
    }
};
