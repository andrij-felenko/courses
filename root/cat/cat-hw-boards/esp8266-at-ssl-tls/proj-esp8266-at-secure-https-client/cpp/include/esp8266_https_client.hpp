#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <cstdint>
#include <memory>
#include <functional>
#include <utility>
#include "uart_ring_buffer.hpp"

/**
 * @brief Структура буфера для розбору та збереження HTTP/HTTPS відповіді.
 */
class HttpResponseBuffer {
public:
    int status_code = 0;
    std::string status_text;
    std::vector<std::pair<std::string, std::string>> headers;
    std::string body;
    bool headers_parsed = false;
    bool is_complete = false;

    /**
     * @brief Очищення стану буфера перед новим HTTPS запитом.
     */
    void clear();

    /**
     * @brief Накопичення фрагментованих даних з кадрів +IPD.
     * @param data Вказівник на байти корисного навантаження.
     * @param length Кількість байтів.
     */
    void append_payload(const uint8_t* data, size_t length);

    /**
     * @brief Перевірка успішності HTTP запиту (статус 2xx).
     */
    bool is_success() const noexcept {
        return status_code >= 200 && status_code < 300;
    }

private:
    std::string raw_headers_stream_;
    void try_parse_headers();
};

/**
 * @brief Перелічення станів скінченного автомата (FSM) HTTPS-клієнта.
 */
enum class HttpsFsmState {
    Idle,
    ConfiguringTls,
    Connecting,
    SendingHeader,
    SendingBody,
    WaitingResponse,
    ReadingIpdPayload,
    Closing,
    Error
};

/**
 * @brief Режими перевірки SSL/TLS сертифікатів (команда AT+CIPSSLCCONF).
 */
enum class TlsAuthMode : uint8_t {
    NoAuth = 0,        ///< Авторизація вимкнена
    VerifyServer = 1,  ///< Перевірка сертифіката сервера (CA)
    ClientCert = 2,    ///< Аутентифікація клієнтським сертифікатом
    MutualAuth = 3     ///< Двостороння TLS аутентифікація
};

/**
 * @brief Параметри конфігурації TLS-сесії ESP8266.
 */
struct TlsConfig {
    TlsAuthMode auth_mode = TlsAuthMode::NoAuth;
    std::string sni_hostname;     ///< Вказання SNI через AT+CIPSSLCSNI
    uint16_t buffer_size = 4096;  ///< Розмір буфера TLS у DRAM модулі через AT+CIPSSLCSZ
    uint32_t handshake_timeout_ms = 15000;
};

class EspHttpsClient;

/**
 * @brief RAII-обгортка для керування з'єднанням TLS (AT+CIPSTART / AT+CIPCLOSE).
 * 
 * Автоматично викликає закриття сокета при виході з області видимості,
 * гарантуючи відсутність витоків пам'яті DRAM в модулі ESP8266 при помилках чи таймаутах.
 */
class TlsContextGuard {
public:
    explicit TlsContextGuard(EspHttpsClient& client);
    ~TlsContextGuard();

    TlsContextGuard(const TlsContextGuard&) = delete;
    TlsContextGuard& operator=(const TlsContextGuard&) = delete;

    TlsContextGuard(TlsContextGuard&& other) noexcept;
    TlsContextGuard& operator=(TlsContextGuard&& other) noexcept;

    /**
     * @brief Скасування автоматичного закриття сокета в деструкторі.
     */
    void release() noexcept { active_ = false; }

private:
    EspHttpsClient* client_ = nullptr;
    bool active_ = false;
};

/**
 * @brief Клас HTTPS-клієнта з інкапсульованим неблокуючим FSM для керування ESP8266.
 */
class EspHttpsClient {
public:
    using UartTxCallback = std::function<void(const uint8_t* data, size_t length)>;
    using TicksCallback = std::function<uint32_t()>;
    using DelayCallback = std::function<void(uint32_t ms)>;

    EspHttpsClient(UartRingBuffer<2048>& rx_buffer,
                    UartTxCallback tx_cb,
                    TicksCallback ticks_cb,
                    DelayCallback delay_cb);

    ~EspHttpsClient();

    /**
     * @brief Відправка AT-команд конфігурації TLS (AT+CIPSSLCCONF, AT+CIPSSLCSNI, AT+CIPSSLCSZ).
     */
    bool configure_tls(const TlsConfig& config);

    /**
     * @brief Виконання HTTPS GET запиту.
     */
    bool execute_get(std::string_view host,
                    uint16_t port,
                    std::string_view path,
                    HttpResponseBuffer& response_out,
                    uint32_t timeout_ms = 15000);

    /**
     * @brief Виконання HTTPS POST запиту з передачею даних.
     */
    bool execute_post(std::string_view host,
                     uint16_t port,
                     std::string_view path,
                     std::string_view content_type,
                     std::string_view body,
                     HttpResponseBuffer& response_out,
                     uint32_t timeout_ms = 15000);

    /**
     * @brief Метод регулярного оновлення станів неблокуючого FSM.
     */
    void update();

    /**
     * @brief Закриття активного з'єднання (AT+CIPCLOSE).
     */
    bool close_session();

    /**
     * @brief Отримання поточного стану FSM.
     */
    HttpsFsmState get_state() const noexcept { return state_; }

private:
    friend class TlsContextGuard;

    bool send_at_cmd(std::string_view cmd, std::string_view expected_reply, uint32_t timeout_ms);
    bool wait_for_reply(std::string_view expected_reply, uint32_t timeout_ms);
    void send_raw(std::string_view data);
    bool start_ssl_connection(std::string_view host, uint16_t port, uint32_t timeout_ms);
    void parse_ipd_stream(HttpResponseBuffer* response, uint32_t timeout_ms);

    UartRingBuffer<2048>& rx_buffer_;
    UartTxCallback tx_cb_;
    TicksCallback ticks_cb_;
    DelayCallback delay_cb_;

    HttpsFsmState state_ = HttpsFsmState::Idle;
    TlsConfig current_tls_config_;
    bool is_connected_ = false;
};
