#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <sstream>
#include <stdexcept>
#include <array>
#include <memory>

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

class ScpiTdrInstrument {
public:
    explicit ScpiTdrInstrument(std::string_view ip, uint16_t port = 5025)
        : m_ip(ip), m_port(port) {
#if defined(_WIN32)
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            throw std::runtime_error("Не вдалося ініціалізувати мережеву бібліотеку Winsock");
        }
#endif
    }

    ~ScpiTdrInstrument() {
        disconnect();
#if defined(_WIN32)
        WSACleanup();
#endif
    }

    void connectToInstrument() {
        m_sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (m_sockfd < 0) {
            throw std::runtime_error("Помилка створення TCP-сокета");
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(m_port);
        inet_pton(AF_INET, m_ip.c_str(), &addr.sin_addr);

        if (connect(m_sockfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            disconnect();
            throw std::runtime_error("Не вдалося підключитися до TDR-приладу за адресою: " + m_ip);
        }

        // Перевірка зв'язку
        std::string idn = query("*IDN?\n");
        std::cout << "[SCPI] Підключено прилад: " << idn;
    }

    void configureTdr(double span_ns, double velocity_factor, bool differential = false) {
        sendCommand(":SENS1:TDR:STAT ON\n");
        sendCommand(":SENS1:TDR:PULS:AMPL 0.200\n");

        if (differential) {
            sendCommand(":SENS1:TDR:MODE DIFF\n");
        } else {
            sendCommand(":SENS1:TDR:MODE SING\n");
        }

        std::ostringstream ss;
        ss << ":TIM:SPAN " << (span_ns * 1e-9) << "\n";
        sendCommand(ss.str());

        ss.str("");
        ss.clear();
        ss << ":CALC1:TDR:VFACT " << velocity_factor << "\n";
        sendCommand(ss.str());

        sendCommand(":CALC1:TDR:UNIT IMP\n");
        sendCommand(":FORM:DATA ASCII\n");
    }

    std::vector<float> readImpedanceProfile() {
        sendCommand(":TRAC:DATA? TRACE1\n");
        std::string rawData = receiveResponse();

        std::vector<float> profile;
        std::stringstream ss(rawData);
        std::string item;

        while (std::getline(ss, item, ',')) {
            try {
                profile.push_back(std::stof(item));
            } catch (...) {
                // Пропуск можливих службових символів
            }
        }

        return profile;
    }

    void disableGenerator() {
        if (m_sockfd >= 0) {
            sendCommand(":SENS1:TDR:STAT OFF\n");
        }
    }

private:
    void sendCommand(std::string_view cmd) {
        if (m_sockfd < 0) throw std::runtime_error("Сокет не підключено");
        ssize_t sent = send(m_sockfd, cmd.data(), cmd.size(), 0);
        if (sent != static_cast<ssize_t>(cmd.size())) {
            throw std::runtime_error("Помилка відправки SCPI команди");
        }
    }

    std::string query(std::string_view queryCmd) {
        sendCommand(queryCmd);
        return receiveResponse();
    }

    std::string receiveResponse() {
        std::string response;
        std::array<char, 4096> buffer;
        ssize_t bytesRead = 0;

        while ((bytesRead = recv(m_sockfd, buffer.data(), buffer.size() - 1, 0)) > 0) {
            buffer[bytesRead] = '\0';
            response.append(buffer.data(), bytesRead);
            if (response.find('\n') != std::string::npos) break;
        }

        return response;
    }

    void disconnect() {
        if (m_sockfd >= 0) {
#if defined(_WIN32)
            closesocket(m_sockfd);
#else
            close(m_sockfd);
#endif
            m_sockfd = -1;
        }
    }

    std::string m_ip;
    uint16_t m_port;
    int m_sockfd{-1};
};
