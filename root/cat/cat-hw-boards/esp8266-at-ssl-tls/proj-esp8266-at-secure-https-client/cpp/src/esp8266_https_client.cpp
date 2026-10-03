#include "esp8266_https_client.hpp"
#include <sstream>
#include <iostream>
#include <cctype>
#include <cstring>

// -----------------------------------------------------------------------------
// Реалізація HttpResponseBuffer
// -----------------------------------------------------------------------------
void HttpResponseBuffer::clear() {
    status_code = 0;
    status_text.clear();
    headers.clear();
    body.clear();
    headers_parsed = false;
    is_complete = false;
    raw_headers_stream_.clear();
}

void HttpResponseBuffer::append_payload(const uint8_t* data, size_t length) {
    if (length == 0) return;

    if (!headers_parsed) {
        raw_headers_stream_.append(reinterpret_cast<const char*>(data), length);
        try_parse_headers();
    } else {
        body.append(reinterpret_cast<const char*>(data), length);
    }
}

void HttpResponseBuffer::try_parse_headers() {
    size_t header_end_pos = raw_headers_stream_.find("\r\n\r\n");
    if (header_end_pos == std::string::npos) {
        return; // Заголовки ще не надійшли повністю
    }

    std::string headers_part = raw_headers_stream_.substr(0, header_end_pos);
    std::string body_part = raw_headers_stream_.substr(header_end_pos + 4);

    std::istringstream stream(headers_part);
    std::string line;

    // Парсинг першого рядка HTTP (Status Line: HTTP/1.1 200 OK)
    if (std::getline(stream, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        
        size_t first_space = line.find(' ');
        if (first_space != std::string::npos) {
            size_t second_space = line.find(' ', first_space + 1);
            if (second_space != std::string::npos) {
                std::string code_str = line.substr(first_space + 1, second_space - first_space - 1);
                status_code = std::stoi(code_str);
                status_text = line.substr(second_space + 1);
            } else {
                std::string code_str = line.substr(first_space + 1);
                status_code = std::stoi(code_str);
            }
        }
    }

    // Парсинг решти заголовків
    while (std::getline(stream, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) continue;

        size_t colon_pos = line.find(':');
        if (colon_pos != std::string::npos) {
            std::string key = line.substr(0, colon_pos);
            std::string value = line.substr(colon_pos + 1);
            
            // Видалення пробілів з початку значення
            size_t val_start = value.find_first_not_of(" \t");
            if (val_start != std::string::npos) {
                value = value.substr(val_start);
            }
            headers.emplace_back(key, value);
        }
    }

    headers_parsed = true;
    body.append(body_part);
}

// -----------------------------------------------------------------------------
// Реалізація TlsContextGuard (RAII)
// -----------------------------------------------------------------------------
TlsContextGuard::TlsContextGuard(EspHttpsClient& client)
    : client_(&client), active_(true) {}

TlsContextGuard::~TlsContextGuard() {
    if (active_ && client_) {
        // Деструктор гарантує виконання AT+CIPCLOSE при виході з функції або виникненні помилок
        client_->close_session();
        active_ = false;
    }
}

TlsContextGuard::TlsContextGuard(TlsContextGuard&& other) noexcept
    : client_(other.client_), active_(other.active_) {
    other.client_ = nullptr;
    other.active_ = false;
}

TlsContextGuard& TlsContextGuard::operator=(TlsContextGuard&& other) noexcept {
    if (this != &other) {
        if (active_ && client_) {
            client_->close_session();
        }
        client_ = other.client_;
        active_ = other.active_;
        other.client_ = nullptr;
        other.active_ = false;
    }
    return *this;
}

// -----------------------------------------------------------------------------
// Реалізація EspHttpsClient
// -----------------------------------------------------------------------------
EspHttpsClient::EspHttpsClient(UartRingBuffer<2048>& rx_buffer,
                               UartTxCallback tx_cb,
                               TicksCallback ticks_cb,
                               DelayCallback delay_cb)
    : rx_buffer_(rx_buffer),
      tx_cb_(std::move(tx_cb)),
      ticks_cb_(std::move(ticks_cb)),
      delay_cb_(std::move(delay_cb)) {}

EspHttpsClient::~EspHttpsClient() {
    if (is_connected_) {
        close_session();
    }
}

void EspHttpsClient::send_raw(std::string_view data) {
    if (tx_cb_) {
        tx_cb_(reinterpret_cast<const uint8_t*>(data.data()), data.size());
    }
}

bool EspHttpsClient::send_at_cmd(std::string_view cmd, std::string_view expected_reply, uint32_t timeout_ms) {
    rx_buffer_.clear();
    send_raw(cmd);
    send_raw("\r\n");
    return wait_for_reply(expected_reply, timeout_ms);
}

bool EspHttpsClient::wait_for_reply(std::string_view expected_reply, uint32_t timeout_ms) {
    const uint32_t start_time = ticks_cb_();
    while ((ticks_cb_() - start_time) < timeout_ms) {
        if (rx_buffer_.find_pattern(expected_reply) >= 0) {
            return true;
        }
        if (rx_buffer_.find_pattern("ERROR\r\n") >= 0 || rx_buffer_.find_pattern("FAIL\r\n") >= 0) {
            state_ = HttpsFsmState::Error;
            return false;
        }
        delay_cb_(1);
    }
    state_ = HttpsFsmState::Error;
    return false; // Таймаут
}

bool EspHttpsClient::configure_tls(const TlsConfig& config) {
    state_ = HttpsFsmState::ConfiguringTls;

    // 1. Конфігурація режиму автентифікації SSL/TLS: AT+CIPSSLCCONF=<auth_mode>
    std::string cmd_conf = "AT+CIPSSLCCONF=" + std::to_string(static_cast<uint8_t>(config.auth_mode));
    if (!send_at_cmd(cmd_conf, "OK\r\n", 3000)) {
        return false;
    }

    // 2. Встановлення SNI (Server Name Indication): AT+CIPSSLCSNI="<hostname>"
    if (!config.sni_hostname.empty()) {
        std::string cmd_sni = "AT+CIPSSLCSNI=\"" + config.sni_hostname + "\"";
        if (!send_at_cmd(cmd_sni, "OK\r\n", 3000)) {
            return false;
        }
    }

    // 3. Налаштування розміру TLS-буфера для запобігання переповненню DRAM: AT+CIPSSLCSZ=<size>
    if (config.buffer_size > 0) {
        std::string cmd_csz = "AT+CIPSSLCSZ=" + std::to_string(config.buffer_size);
        if (!send_at_cmd(cmd_csz, "OK\r\n", 3000)) {
            return false;
        }
    }

    current_tls_config_ = config;
    state_ = HttpsFsmState::Idle;
    return true;
}

bool EspHttpsClient::start_ssl_connection(std::string_view host, uint16_t port, uint32_t timeout_ms) {
    state_ = HttpsFsmState::Connecting;
    std::string cmd = "AT+CIPSTART=\"SSL\",\"" + std::string(host) + "\"," + std::to_string(port);
    
    rx_buffer_.clear();
    send_raw(cmd);
    send_raw("\r\n");

    const uint32_t start_time = ticks_cb_();
    while ((ticks_cb_() - start_time) < timeout_ms) {
        if (rx_buffer_.find_pattern("CONNECT\r\n") >= 0 || rx_buffer_.find_pattern("OK\r\n") >= 0) {
            is_connected_ = true;
            state_ = HttpsFsmState::Idle;
            return true;
        }
        if (rx_buffer_.find_pattern("CLOSED\r\n") >= 0 || rx_buffer_.find_pattern("ERROR\r\n") >= 0) {
            state_ = HttpsFsmState::Error;
            return false;
        }
        delay_cb_(2);
    }

    state_ = HttpsFsmState::Error;
    return false;
}

bool EspHttpsClient::close_session() {
    if (!is_connected_) {
        return true;
    }

    state_ = HttpsFsmState::Closing;
    bool success = send_at_cmd("AT+CIPCLOSE", "OK\r\n", 3000);
    is_connected_ = false;
    state_ = HttpsFsmState::Idle;
    return success;
}

bool EspHttpsClient::execute_get(std::string_view host,
                                uint16_t port,
                                std::string_view path,
                                HttpResponseBuffer& response_out,
                                uint32_t timeout_ms) {
    response_out.clear();

    // Захист сесії через RAII: деструктор викликає close_session() у разі виходу за межі функції
    TlsContextGuard guard(*this);

    // Оновлення SNI під поточний хост
    if (current_tls_config_.sni_hostname != host) {
        TlsConfig cfg = current_tls_config_;
        cfg.sni_hostname = std::string(host);
        if (!configure_tls(cfg)) {
            return false;
        }
    }

    if (!start_ssl_connection(host, port, timeout_ms)) {
        return false;
    }

    // Формування заголовків HTTPS GET
    std::string http_req = "GET " + std::string(path) + " HTTP/1.1\r\n";
    http_req += "Host: " + std::string(host) + "\r\n";
    http_req += "User-Agent: ESP8266-AT-Client/2.0\r\n";
    http_req += "Connection: close\r\n\r\n";

    // Відправка AT+CIPSEND для резервування довжини кадру
    state_ = HttpsFsmState::SendingHeader;
    std::string cmd_send = "AT+CIPSEND=" + std::to_string(http_req.size());
    if (!send_at_cmd(cmd_send, ">", 3000)) {
        return false;
    }

    // Передача корисного навантаження HTTP запиту
    rx_buffer_.clear();
    send_raw(http_req);
    if (!wait_for_reply("SEND OK\r\n", 5000)) {
        return false;
    }

    // Потоковий збір кадрів +IPD з вичитанням відповіді
    parse_ipd_stream(&response_out, timeout_ms);
    return response_out.headers_parsed;
}

bool EspHttpsClient::execute_post(std::string_view host,
                                 uint16_t port,
                                 std::string_view path,
                                 std::string_view content_type,
                                 std::string_view body,
                                 HttpResponseBuffer& response_out,
                                 uint32_t timeout_ms) {
    response_out.clear();
    TlsContextGuard guard(*this);

    if (current_tls_config_.sni_hostname != host) {
        TlsConfig cfg = current_tls_config_;
        cfg.sni_hostname = std::string(host);
        if (!configure_tls(cfg)) {
            return false;
        }
    }

    if (!start_ssl_connection(host, port, timeout_ms)) {
        return false;
    }

    std::string http_req = "POST " + std::string(path) + " HTTP/1.1\r\n";
    http_req += "Host: " + std::string(host) + "\r\n";
    http_req += "User-Agent: ESP8266-AT-Client/2.0\r\n";
    http_req += "Content-Type: " + std::string(content_type) + "\r\n";
    http_req += "Content-Length: " + std::to_string(body.size()) + "\r\n";
    http_req += "Connection: close\r\n\r\n";
    http_req += std::string(body);

    state_ = HttpsFsmState::SendingBody;
    std::string cmd_send = "AT+CIPSEND=" + std::to_string(http_req.size());
    if (!send_at_cmd(cmd_send, ">", 3000)) {
        return false;
    }

    rx_buffer_.clear();
    send_raw(http_req);
    if (!wait_for_reply("SEND OK\r\n", 5000)) {
        return false;
    }

    parse_ipd_stream(&response_out, timeout_ms);
    return response_out.headers_parsed;
}

void EspHttpsClient::parse_ipd_stream(HttpResponseBuffer* response, uint32_t timeout_ms) {
    state_ = HttpsFsmState::WaitingResponse;
    const uint32_t start_time = ticks_cb_();

    while ((ticks_cb_() - start_time) < timeout_ms) {
        // Пошук маркера +IPD, у кільцевому буфері UART
        int ipd_pos = rx_buffer_.find_pattern("+IPD,");
        if (ipd_pos >= 0) {
            rx_buffer_.skip(static_cast<size_t>(ipd_pos) + 5); // Пропускаємо "+IPD,"

            // Вичитання довжини кадру до двоеточія ':'
            std::string len_str;
            uint8_t ch = 0;
            const uint32_t len_read_start = ticks_cb_();
            bool colon_found = false;

            while ((ticks_cb_() - len_read_start) < 2000) {
                if (rx_buffer_.pop(ch)) {
                    if (ch == ':') {
                        colon_found = true;
                        break;
                    }
                    if (std::isdigit(ch)) {
                        len_str.push_back(static_cast<char>(ch));
                    }
                } else {
                    delay_cb_(1);
                }
            }

            if (colon_found && !len_str.empty()) {
                size_t payload_len = std::stoul(len_str);
                state_ = HttpsFsmState::ReadingIpdPayload;

                // Читання корисного навантаження кадру +IPD
                std::vector<uint8_t> payload_buf(payload_len);
                size_t read_accumulated = 0;
                const uint32_t payload_read_start = ticks_cb_();

                while (read_accumulated < payload_len && (ticks_cb_() - payload_read_start) < 5000) {
                    size_t chunk = rx_buffer_.pop_bytes(payload_buf.data() + read_accumulated, payload_len - read_accumulated);
                    read_accumulated += chunk;
                    if (chunk == 0) {
                        delay_cb_(1);
                    }
                }

                if (response && read_accumulated > 0) {
                    response->append_payload(payload_buf.data(), read_accumulated);
                }
            }
        }

        if (rx_buffer_.find_pattern("CLOSED\r\n") >= 0) {
            is_connected_ = false;
            if (response) {
                response->is_complete = true;
            }
            break;
        }

        delay_cb_(2);
    }

    state_ = HttpsFsmState::Idle;
}

void EspHttpsClient::update() {
    // Неблокуючий фоновий метод для підтримки життєвого циклу
    if (state_ == HttpsFsmState::Error) {
        if (is_connected_) {
            close_session();
        }
    }
}
