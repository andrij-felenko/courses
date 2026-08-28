#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <thread>
#include <format>
#include <expected>
#include <stdexcept>
#include <span>
#include <charconv>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  using socket_handle_t = SOCKET;
  constexpr socket_handle_t invalid_socket = INVALID_SOCKET;
  inline int close_socket(socket_handle_t s) { return closesocket(s); }
#else
  #include <unistd.h>
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  using socket_handle_t = int;
  constexpr socket_handle_t invalid_socket = -1;
  inline int close_socket(socket_handle_t s) { return close(s); }
#endif

// RAII обгортка мережевої сесії керування SCPI
class ScpiSession {
public:
    ScpiSession(std::string_view ip, uint16_t port) {
#if defined(_WIN32)
        WSADATA wsa_data;
        if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
            throw std::runtime_error("Не вдалося ініціалізувати підсистему WSAStartup");
        }
        wsa_initialized_ = true;
#endif
        sock_ = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock_ == invalid_socket) {
            cleanup();
            throw std::runtime_error("Помилка створення сокета TCP");
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        std::string ip_str(ip);
        inet_pton(AF_INET, ip_str.c_str(), &addr.sin_addr);

        if (::connect(sock_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            cleanup();
            throw std::runtime_error(std::format("Не вдалося підключитися до приладу {}:{}", ip, port));
        }
    }

    ~ScpiSession() noexcept {
        try {
            // Безпечне вимкнення силового каналу в деструкторі за будь-яких умов
            send("OUTP OFF\n");
        } catch (...) {}
        cleanup();
    }

    ScpiSession(const ScpiSession&) = delete;
    ScpiSession& operator=(const ScpiSession&) = delete;
    ScpiSession(ScpiSession&& other) noexcept : sock_(other.sock_) {
        other.sock_ = invalid_socket;
    }

    void send(std::string_view cmd) {
        if (sock_ == invalid_socket) {
            throw std::runtime_error("Спроба запису в закритий сокет");
        }
        size_t total = 0;
        while (total < cmd.size()) {
            auto sent = ::send(sock_, cmd.data() + total, static_cast<int>(cmd.size() - total), 0);
            if (sent <= 0) {
                throw std::runtime_error("Помилка передачі команди SCPI через сокет");
            }
            total += static_cast<size_t>(sent);
        }
    }

    std::string query(std::string_view cmd) {
        send(cmd);
        std::vector<char> buffer(256);
        auto received = ::recv(sock_, buffer.data(), static_cast<int>(buffer.size() - 1), 0);
        if (received <= 0) {
            throw std::runtime_error("Помилка отримання відповіді або таймаут зв'язку SCPI");
        }
        buffer[received] = '\0';
        std::string res(buffer.data());
        while (!res.empty() && (res.back() == '\r' || res.back() == '\n')) {
            res.pop_back();
        }
        return res;
    }

    std::expected<double, std::string> measure_current() {
        try {
            auto res = query("MEAS:CURR?\n");
            double val = 0.0;
            auto [ptr, ec] = std::from_chars(res.data(), res.data() + res.size(), val);
            if (ec == std::errc()) {
                return val;
            }
            return std::unexpected("Не вдалося розпарсити числове значення струму: " + res);
        } catch (const std::exception& e) {
            return std::unexpected(e.what());
        }
    }

private:
    void cleanup() noexcept {
        if (sock_ != invalid_socket) {
            close_socket(sock_);
            sock_ = invalid_socket;
        }
#if defined(_WIN32)
        if (wsa_initialized_) {
            WSACleanup();
            wsa_initialized_ = false;
        }
#endif
    }

    socket_handle_t sock_{invalid_socket};
#if defined(_WIN32)
    bool wsa_initialized_{false};
#endif
};

struct BringupConfig {
    double target_voltage_v = 3.30;
    double current_limit_a = 0.050;       // Апаратний ліміт 50 мА
    double max_safe_quiescent_a = 0.035;  // Поріг тривоги струму спокою 35 мА
    double step_voltage_v = 0.20;
    std::chrono::milliseconds step_delay{100};
};

bool execute_bringup(ScpiSession& psu, const BringupConfig& cfg) {
    std::cout << std::format("Ідентифікатор обладнання: {}\n", psu.query("*IDN?\n"));

    psu.send("*RST\n");
    std::this_thread::sleep_for(std::chrono::milliseconds(200));

    // Фіксуємо апаратний ліміт струму в блоці живлення
    psu.send(std::format("CURR {:.4f}\n", cfg.current_limit_a));
    psu.send("VOLT 0.0\n");
    psu.send("OUTP ON\n");
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << std::format("Початок керованого підйому напруги до {:.2f} В (Ліміт: {:.1f} мА)...\n",
                             cfg.target_voltage_v, cfg.current_limit_a * 1000.0);

    for (double v = cfg.step_voltage_v; v <= cfg.target_voltage_v + 0.001; v += cfg.step_voltage_v) {
        psu.send(std::format("VOLT {:.3f}\n", v));
        std::this_thread::sleep_for(cfg.step_delay);

        auto i_meas = psu.measure_current();
        if (!i_meas) {
            std::cerr << "Помилка зчитування струму: " << i_meas.error() << "\n";
            psu.send("OUTP OFF\n");
            return false;
        }

        double current = *i_meas;
        std::cout << std::format("  Напруга: {:5.2f} В | Струм споживання: {:6.2f} мА\n",
                                 v, current * 1000.0);

        if (current > cfg.max_safe_quiescent_a) {
            std::cerr << std::format("\n[АВАРІЯ] Струм холостого ходу ({:.2f} мА) перевищив норму ({:.2f} мА) при {:.2f} В!\n",
                                     current * 1000.0, cfg.max_safe_quiescent_a * 1000.0, v);
            psu.send("OUTP OFF\n");
            double r_equiv = v / current;
            std::cerr << std::format("Розрахунковий опір витоку кола: {:.2f} Ом\n", r_equiv);
            return false;
        }
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));
    auto final_i = psu.measure_current().value_or(0.0);
    std::cout << std::format("\nСтабільний режим підтверджено. Фінальний струм спокою: {:.2f} мА\n",
                             final_i * 1000.0);
    return true;
}

int main(int argc, char* argv[]) {
    const std::string ip = (argc > 1) ? argv[1] : "192.168.1.105";
    constexpr uint16_t port = 5025;

    try {
        ScpiSession psu(ip, port);
        BringupConfig cfg{
            .target_voltage_v = 3.30,
            .current_limit_a = 0.050,
            .max_safe_quiescent_a = 0.035,
            .step_voltage_v = 0.20,
            .step_delay = std::chrono::milliseconds(100)
        };

        if (!execute_bringup(psu, cfg)) {
            std::cout << "Запуск зупинено через критичне відхилення струму. Перевірте монтаж.\n";
            return 1;
        }
        std::cout << "Перший запуск плати успішно завершено. Живлення залишається увімкненим.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Критична системна помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
