#include <iostream>
#include <vector>
#include <chrono>
#include <cstring>
#include <span>
#include <unistd.h>
#include <arpa/inet.h>

constexpr int PORT = 8080;
constexpr size_t CHUNK_SIZE = 1024;
constexpr size_t BUFFER_SIZE = 4096;

// RAII-обгортка для сокета
class Socket {
    int fd = -1;
public:
    explicit Socket(int fd) : fd(fd) {}
    ~Socket() { if (fd != -1) close(fd); }
    
    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;
    
    Socket(Socket&& other) noexcept : fd(other.fd) { other.fd = -1; }
    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            if (fd != -1) close(fd);
            fd = other.fd;
            other.fd = -1;
        }
        return *this;
    }
    
    int get() const { return fd; }
};

void handle_client(Socket client_sock) {
    std::vector<uint8_t> buffer(BUFFER_SIZE);
    std::vector<uint8_t> chunk_buffer;
    chunk_buffer.reserve(CHUNK_SIZE);
    
    uint64_t total_bytes = 0;
    uint32_t expected_seq = 0;
    
    auto last_report_time = std::chrono::steady_clock::now();
    uint64_t bytes_since_report = 0;
    
    while (true) {
        ssize_t bytes_read = recv(client_sock.get(), buffer.data(), buffer.size(), 0);
        if (bytes_read <= 0) break;
        
        std::span<const uint8_t> data_span(buffer.data(), bytes_read);
        for (uint8_t byte : data_span) {
            chunk_buffer.push_back(byte);
            
            if (chunk_buffer.size() == CHUNK_SIZE) {
                uint8_t calculated_checksum = 0;
                for (size_t i = 0; i < CHUNK_SIZE - 1; ++i) {
                    calculated_checksum ^= chunk_buffer[i];
                }
                
                if (calculated_checksum != chunk_buffer.back()) {
                    std::cerr << "Помилка КС! Очікувано: " << static_cast<int>(calculated_checksum)
                              << ", Отримано: " << static_cast<int>(chunk_buffer.back()) << "\n";
                }
                
                uint32_t seq = 0;
                std::memcpy(&seq, chunk_buffer.data(), sizeof(seq));
                
                if (seq != expected_seq) {
                    std::cerr << "Втрата пакетів! Очікуваний seq: " << expected_seq 
                              << ", Отриманий: " << seq << "\n";
                    expected_seq = seq;
                }
                
                expected_seq++;
                total_bytes += CHUNK_SIZE;
                bytes_since_report += CHUNK_SIZE;
                chunk_buffer.clear();
                
                auto current_time = std::chrono::steady_clock::now();
                std::chrono::duration<double> elapsed = current_time - last_report_time;
                
                if (elapsed.count() >= 1.0) {
                    double speed_kb = (bytes_since_report / 1024.0) / elapsed.count();
                    std::cout << "Отримано: " << total_bytes / 1024.0 << " KB, "
                              << "Швидкість: " << speed_kb << " KB/s\n";
                    last_report_time = current_time;
                    bytes_since_report = 0;
                }
            }
        }
    }
}

int main() {
    Socket server_sock(socket(AF_INET, SOCK_STREAM, 0));
    if (server_sock.get() < 0) {
        perror("socket");
        return 1;
    }
    
    int opt = 1;
    setsockopt(server_sock.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    if (bind(server_sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        perror("bind");
        return 1;
    }
    
    if (listen(server_sock.get(), 5) < 0) {
        perror("listen");
        return 1;
    }
    
    std::cout << "Сервер слухає на порту " << PORT << "...\n";
    
    while (true) {
        int fd = accept(server_sock.get(), nullptr, nullptr);
        if (fd >= 0) {
            std::cout << "Нове з'єднання\n";
            handle_client(Socket(fd));
            std::cout << "Клієнт відключився\n";
        }
    }
    
    return 0;
}
