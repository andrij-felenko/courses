#include <iostream>
#include <array>
#include <vector>
#include <string>
#include <chrono>
#include <cmath>
#include <random>
#include <cstring>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
#else
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  #include <unistd.h>
#endif

// Структура фізичного стану літального апарата
struct VehicleState {
    double timestamp_s{0.0};
    std::array<double, 3> pos_ned_m{0.0, 0.0, 0.0};
    std::array<double, 3> vel_ned_mps{0.0, 0.0, 0.0};
    std::array<double, 3> accel_body_mps2{0.0, 0.0, 0.0};
    std::array<double, 3> gyro_body_radps{0.0, 0.0, 0.0};
    std::array<double, 4> quat_nb{1.0, 0.0, 0.0, 0.0};
};

// Генератор шуму та випадкового блукання зміщення Гаусса-Маркова
class SensorNoiseModel {
public:
    SensorNoiseModel(double std_dev_noise, double std_dev_bias, double tau_s)
        : noise_dist_(0.0, std_dev_noise),
          bias_dist_(0.0, std_dev_bias),
          tau_(tau_s),
          std_bias_(std_dev_bias),
          bias_(0.0) {}

    double update(double true_value, double dt) {
        // Оновлення дискретного процесу випадкового дрейфу 1-го порядку
        double drift_step = std_bias_ * std::sqrt(2.0 * dt / tau_) * unit_norm_dist_(rng_);
        bias_ = (1.0 - dt / tau_) * bias_ + drift_step;
        
        // Додавання високочастотного білого шуму
        double white_noise = noise_dist_(rng_);
        return true_value + bias_ + white_noise;
    }

private:
    std::mt19937_64 rng_{1337};
    std::normal_distribution<double> noise_dist_;
    std::normal_distribution<double> bias_dist_;
    std::normal_distribution<double> unit_norm_dist_{0.0, 1.0};
    double tau_;
    double std_bias_;
    double bias_;
};

// Безпечна RAII-обгортка мережевого UDP-сокета
class UdpSocket {
public:
    UdpSocket(int local_port, const std::string& remote_ip, int remote_port)
        : remote_port_(remote_port) {
#if defined(_WIN32)
        WSADATA wsa;
        WSAStartup(MAKEWORD(2, 2), &wsa);
#endif
        sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
        
        sockaddr_in local_addr{};
        local_addr.sin_family = AF_INET;
        local_addr.sin_addr.s_addr = INADDR_ANY;
        local_addr.sin_port = htons(local_port);
        bind(sockfd_, reinterpret_cast<sockaddr*>(&local_addr), sizeof(local_addr));

        std::memset(&remote_addr_, 0, sizeof(remote_addr_));
        remote_addr_.sin_family = AF_INET;
        remote_addr_.sin_port = htons(remote_port);
        inet_pton(AF_INET, remote_ip.c_str(), &remote_addr_.sin_addr);
    }

    ~UdpSocket() {
#if defined(_WIN32)
        closesocket(sockfd_);
        WSACleanup();
#else
        close(sockfd_);
#endif
    }

    bool receive_packet(std::string& out_buffer) {
        std::array<char, 2048> buf{};
        sockaddr_in src_addr{};
        socklen_t addr_len = sizeof(src_addr);
        auto bytes = recvfrom(sockfd_, buf.data(), buf.size() - 1, 0,
                              reinterpret_cast<sockaddr*>(&src_addr), &addr_len);
        if (bytes > 0) {
            buf[bytes] = '\0';
            out_buffer = buf.data();
            return true;
        }
        return false;
    }

    void send_packet(const std::string& data) {
        sendto(sockfd_, data.data(), data.size(), 0,
               reinterpret_cast<sockaddr*>(&remote_addr_), sizeof(remote_addr_));
    }

private:
#if defined(_WIN32)
    SOCKET sockfd_;
#else
    int sockfd_;
#endif
    int remote_port_;
    sockaddr_in remote_addr_;
};

// Головна функція запуску мосту симуляції
int main() {
    std::cout << "[SITL Bridge] Запуск UDP-мосту на портах 9003 -> 9002...\n";

    // Слухаємо актуатори на порту 9003, надсилаємо сенсори на 9002
    UdpSocket bridge_socket(9003, "127.0.0.1", 9002);

    VehicleState state{};
    SensorNoiseModel accel_noise(0.08, 0.005, 300.0);  // Шум акселерометра 0.08 м/с², тау 300 с
    SensorNoiseModel gyro_noise(0.003, 0.0002, 200.0); // Шум гіроскопа 0.003 рад/с
    SensorNoiseModel baro_noise(0.4, 0.05, 600.0);     // Шум барометра 0.4 Па

    constexpr double dt = 0.0025; // 400 Гц крок фізики

    while (true) {
        std::string rx_packet;
        if (!bridge_socket.receive_packet(rx_packet)) {
            continue;
        }

        // 1. Інтегрування простої моделі динаміки польоту
        state.timestamp_s += dt;
        
        // Симуляція прискорення (висіння при компенсації сили тяжіння)
        double true_acc_z = -9.80665; // Акселерометр у спокої фіксує +1g вгору
        double noisy_acc_x = accel_noise.update(0.0, dt);
        double noisy_acc_y = accel_noise.update(0.0, dt);
        double noisy_acc_z = accel_noise.update(true_acc_z, dt);

        double noisy_gyro_x = gyro_noise.update(0.0, dt);
        double noisy_gyro_y = gyro_noise.update(0.0, dt);
        double noisy_gyro_z = gyro_noise.update(0.0, dt);

        // Розрахунок статичного тиску за стандартною атмосферою
        double alt_m = -state.pos_ned_m[2]; // Z у системі NED спрямовано вниз
        double true_pressure_pa = 101325.0 * std::pow(1.0 - 0.0065 * alt_m / 288.15, 5.255);
        double noisy_pressure_pa = baro_noise.update(true_pressure_pa, dt);

        // 2. Формування вихідного JSON-пакета для ArduPilot SITL
        std::string tx_json = "{"
            "\"timestamp\":" + std::to_string(state.timestamp_s) + ","
            "\"imu\":{\"gyro\":[" + std::to_string(noisy_gyro_x) + "," + 
                                    std::to_string(noisy_gyro_y) + "," + 
                                    std::to_string(noisy_gyro_z) + "],"
                     "\"accel_body\":[" + std::to_string(noisy_acc_x) + "," + 
                                          std::to_string(noisy_acc_y) + "," + 
                                          std::to_string(noisy_acc_z) + "]},"
            "\"baro\":{\"pressure_pa\":" + std::to_string(noisy_pressure_pa) + "},"
            "\"position\":[" + std::to_string(state.pos_ned_m[0]) + "," + 
                               std::to_string(state.pos_ned_m[1]) + "," + 
                               std::to_string(state.pos_ned_m[2]) + "]"
        "}\n";

        bridge_socket.send_packet(tx_json);
    }
    return 0;
}
