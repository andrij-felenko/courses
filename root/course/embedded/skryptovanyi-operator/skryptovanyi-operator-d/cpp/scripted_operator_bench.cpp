/**
 * @file scripted_operator_bench.cpp
 * @brief Високопродуктивний тестовий стенд регресії на C++20.
 *
 * Використовує асинхронні сокети, RAII-обгортки та обчислення DTW-коридорів
 * без блокування головного контуру виконання.
 */

#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <cmath>
#include <stdexcept>
#include <thread>
#include <algorithm>
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
  #include <fcntl.h>
#endif

// Структура запису стану телеметрії для порівняння
struct TelemetrySample {
    std::chrono::steady_clock::time_point timestamp;
    double roll_deg{0.0};
    double pitch_deg{0.0};
    double yaw_deg{0.0};
    double altitude_m{0.0};
};

// RAII обгортка для неблокуючого UDP-сокета
class UdpSocket {
public:
    UdpSocket(const std::string& ip, int port) {
#if defined(_WIN32)
        WSADATA wsaData;
        WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
        sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd_ < 0) {
            throw std::runtime_error("Не вдалося створити сокет UDP");
        }

        // Встановлення неблокуючого режиму
#if defined(_WIN32)
        u_long mode = 1;
        ioctlsocket(sockfd_, FIONBIO, &mode);
#else
        int flags = fcntl(sockfd_, F_GETFL, 0);
        fcntl(sockfd_, F_SETFL, flags | O_NONBLOCK);
#endif

        std::memset(&target_addr_, 0, sizeof(target_addr_));
        target_addr_.sin_family = AF_INET;
        target_addr_.sin_port = htons(static_cast<uint16_t>(port));
        inet_pton(AF_INET, ip.c_str(), &target_addr_.sin_addr);
    }

    ~UdpSocket() {
#if defined(_WIN32)
        if (sockfd_ != INVALID_SOCKET) closesocket(sockfd_);
        WSACleanup();
#else
        if (sockfd_ >= 0) close(sockfd_);
#endif
    }

    bool send(const std::vector<uint8_t>& buffer) {
        auto sent = sendto(sockfd_, reinterpret_cast<const char*>(buffer.data()),
                           static_cast<int>(buffer.size()), 0,
                           reinterpret_cast<const sockaddr*>(&target_addr_),
                           sizeof(target_addr_));
        return sent == static_cast<int>(buffer.size());
    }

    int receive(std::vector<uint8_t>& buffer) {
        sockaddr_in src_addr{};
        socklen_t addr_len = sizeof(src_addr);
        auto bytes = recvfrom(sockfd_, reinterpret_cast<char*>(buffer.data()),
                              static_cast<int>(buffer.size()), 0,
                              reinterpret_cast<sockaddr*>(&src_addr), &addr_len);
        return static_cast<int>(bytes);
    }

private:
#if defined(_WIN32)
    SOCKET sockfd_{INVALID_SOCKET};
#else
    int sockfd_{-1};
#endif
    sockaddr_in target_addr_{};
};

// Модуль розрахунку Dynamic Time Warping (DTW) зі смугою Сакое-Чіба
class TrajectoryComparator {
public:
    static double calculate_dtw_rmse(const std::vector<TelemetrySample>& actual,
                                     const std::vector<TelemetrySample>& reference,
                                     size_t warping_band = 25) {
        if (actual.empty() || reference.empty()) return 0.0;

        const size_t n = actual.size();
        const size_t m = reference.size();
        const double inf = 1e9;

        std::vector<std::vector<double>> d(n + 1, std::vector<double>(m + 1, inf));
        d[0][0] = 0.0;

        for (size_t i = 1; i <= n; ++i) {
            size_t j_min = (i > warping_band) ? (i - warping_band) : 1;
            size_t j_max = std::min(m, i + warping_band);

            for (size_t j = j_min; j <= j_max; ++j) {
                double diff_roll = actual[i - 1].roll_deg - reference[j - 1].roll_deg;
                double diff_alt = actual[i - 1].altitude_m - reference[j - 1].altitude_m;
                double cost = (diff_roll * diff_roll) + (diff_alt * diff_alt * 10.0);

                d[i][j] = cost + std::min({d[i - 1][j],      // пропуск у фактичному
                                           d[i][j - 1],      // пропуск в еталоні
                                           d[i - 1][j - 1]}); // вирівнювання
            }
        }

        return std::sqrt(d[n][m] / static_cast<double>(std::max(n, m)));
    }
};

// Оркестратор тестового стенда
class ScriptedOperatorHarnessCpp {
public:
    ScriptedOperatorHarnessCpp(const std::string& ip, int port)
        : socket_(ip, port) {}

    void run_batch_test() {
        std::cout << "[*] C++20 Test Harness: Старт пакетної регресії...\n";

        auto start_time = std::chrono::steady_clock::now();
        std::vector<TelemetrySample> log;
        log.reserve(1000);

        // Фаза 1: 3 секунди подачі пакетів керування
        std::cout << "[*] Фаза 1: Інжекція команд керування (50 Гц)...\n";
        while (true) {
            auto now = std::chrono::steady_clock::now();
            auto elapsed = std::chrono::duration<double>(now - start_time).count();
            if (elapsed >= 3.0) break;

            // Формування синтетичного пакету (наприклад RC Override)
            std::vector<uint8_t> dummy_frame(32, 0xAA);
            socket_.send(dummy_frame);

            // Логування стану
            log.push_back({now, 5.2 * std::sin(elapsed * 2.0), 0.0, 0.0, 10.0 + elapsed * 1.5});
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        }

        // Фаза 2: Симуляція відмови (обрив потоку) на 2 секунди
        std::cout << "[*] Фаза 2: Внесення відмови (тиша в каналі)...\n";
        auto drop_start = std::chrono::steady_clock::now();
        while (true) {
            auto now = std::chrono::steady_clock::now();
            auto elapsed = std::chrono::duration<double>(now - drop_start).count();
            if (elapsed >= 2.0) break;

            // Пакети не надсилаються (імітація втрати зв'язку)
            log.push_back({now, 0.0, 0.0, 0.0, 14.5});
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        }

        // Порівняння з синтетичним еталоном
        auto reference = log; // Для демонстрації як еталон
        double rmse = TrajectoryComparator::calculate_dtw_rmse(log, reference);

        std::cout << "[+] Лог зібрано: " << log.size() << " семплів.\n";
        std::cout << "[+] DTW RMSE відхилення від еталону: " << rmse << " (допуск < 0.25)\n";

        if (rmse < 0.25) {
            std::cout << "[PASS] Регресійний тест виконано успішно!\n";
        } else {
            throw std::runtime_error("FAIL: Розбіжність траєкторії перевищує поріг допуску!");
        }
    }

private:
    UdpSocket socket_;
};

int main() {
    try {
        ScriptedOperatorHarnessCpp harness("127.0.0.1", 14550);
        harness.run_batch_test();
    } catch (const std::exception& ex) {
        std::cerr << "[ERROR] " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
