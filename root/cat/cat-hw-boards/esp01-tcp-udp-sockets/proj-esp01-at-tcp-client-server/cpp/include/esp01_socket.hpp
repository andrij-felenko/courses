#ifndef ESP01_SOCKET_HPP
#define ESP01_SOCKET_HPP

#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <cstdint>
#include <cstddef>
#include <optional>
#include <functional>

// Структура для зберігання отриманого від сокета пакета даних
struct SocketPacket {
    int link_id{-1};
    std::vector<uint8_t> payload;
};

// Буфер для накопичення прийнятих даних за ID сокета
class SocketBuffer {
public:
    explicit SocketBuffer(size_t max_capacity = 2048);
    
    bool append(int link_id, const uint8_t* data, size_t length);
    std::optional<SocketPacket> pop_packet();
    void clear_link(int link_id);

private:
    struct Entry {
        int link_id;
        std::vector<uint8_t> data;
    };
    size_t capacity_;
    std::vector<Entry> queue_;
};

// Неблокуючий драйвер UART інтерфейсу
class ESP01UartDriver {
public:
    ESP01UartDriver() = default;
    virtual ~ESP01UartDriver() = default;

    virtual bool write_bytes(const uint8_t* data, size_t length) = 0;
    virtual size_t read_bytes(uint8_t* buffer, size_t max_length) = 0;
    virtual void flush_rx() = 0;
};

// Типи мережевих протоколів
enum class TransportProtocol {
    TCP,
    UDP
};

// Подія змінення стану сокета
enum class SocketEvent {
    Connected,
    Disconnected,
    DataReceived
};

// Головний клас-абстракція сокетного клієнта й сервера на ESP-01
class ESP01SocketClientServer {
public:
    explicit ESP01SocketClientServer(ESP01UartDriver& uart_driver);
    ~ESP01SocketClientServer() = default;

    // Ініціалізація модуля та налаштування режиму багатьох з'єднань (CIPMUX=1)
    bool begin();

    // Запуск TCP/UDP сервера на вказаному порту
    bool start_server(uint16_t port);
    bool stop_server();

    // Підключення до віддаленого сервера як клієнт
    std::optional<int> connect_client(TransportProtocol proto, std::string_view host, uint16_t port);

    // Відправка даних через відкрите з'єднання
    bool send_data(int link_id, const uint8_t* data, size_t length);

    // Закриття конкретного сокета
    bool close_link(int link_id);

    // Обробник оновлення стану та розбору вхідного UART потоку
    void poll();

    // Отримання чергового пакета даних
    std::optional<SocketPacket> read_packet();

    // Перевірка стану підключення лінку
    bool is_link_active(int link_id) const;

private:
    enum class RxState {
        Idle,
        ParsingIpdHeader,
        ReadingIpdPayload
    };

    ESP01UartDriver& uart_;
    SocketBuffer rx_buffer_;
    std::array<bool, 5> active_links_{false, false, false, false, false};
    std::string rx_line_buffer_;
    
    // Стан парсера +IPD
    RxState parser_state_{RxState::Idle};
    int current_ipd_link_{-1};
    size_t current_ipd_expected_{0};
    size_t current_ipd_received_{0};
    std::vector<uint8_t> current_ipd_payload_;

    bool send_at_command(std::string_view cmd, std::string_view expected_reply, uint32_t timeout_ms = 1000);
    void process_rx_char(char ch);
    void process_completed_line(std::string_view line);
};

#endif // ESP01_SOCKET_HPP
