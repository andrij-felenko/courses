#include "esp01_socket.hpp"
#include <iostream>
#include <sstream>
#include <algorithm>
#include <chrono>
#include <thread>

SocketBuffer::SocketBuffer(size_t max_capacity)
    : capacity_(max_capacity) {}

bool SocketBuffer::append(int link_id, const uint8_t* data, size_t length) {
    if (length == 0 || data == nullptr) {
        return false;
    }
    queue_.push_back({link_id, std::vector<uint8_t>(data, data + length)});
    return true;
}

std::optional<SocketPacket> SocketBuffer::pop_packet() {
    if (queue_.empty()) {
        return std::nullopt;
    }
    Entry front = std::move(queue_.front());
    queue_.erase(queue_.begin());
    return SocketPacket{front.link_id, std::move(front.data)};
}

void SocketBuffer::clear_link(int link_id) {
    auto it = std::remove_if(queue_.begin(), queue_.end(),
                             [link_id](const Entry& e) { return e.link_id == link_id; });
    queue_.erase(it, queue_.end());
}

ESP01SocketClientServer::ESP01SocketClientServer(ESP01UartDriver& uart_driver)
    : uart_(uart_driver) {}

bool ESP01SocketClientServer::begin() {
    uart_.flush_rx();
    // Тест готовності модуля
    if (!send_at_command("AT", "OK", 500)) {
        return false;
    }
    // Включення режиму багатьох з'єднань
    if (!send_at_command("AT+CIPMUX=1", "OK", 1000)) {
        return false;
    }
    return true;
}

bool ESP01SocketClientServer::start_server(uint16_t port) {
    std::ostringstream ss;
    ss << "AT+CIPSERVER=1," << port;
    return send_at_command(ss.str(), "OK", 2000);
}

bool ESP01SocketClientServer::stop_server() {
    return send_at_command("AT+CIPSERVER=0", "OK", 2000);
}

std::optional<int> ESP01SocketClientServer::connect_client(TransportProtocol proto, std::string_view host, uint16_t port) {
    // Шукаємо вільний ідентифікатор лінку (від 0 до 4)
    int link_id = -1;
    for (size_t i = 0; i < active_links_.size(); ++i) {
        if (!active_links_[i]) {
            link_id = static_cast<int>(i);
            break;
        }
    }
    if (link_id == -1) {
        return std::nullopt;
    }

    std::ostringstream ss;
    const char* proto_str = (proto == TransportProtocol::TCP) ? "TCP" : "UDP";
    ss << "AT+CIPSTART=" << link_id << ",\"" << proto_str << "\",\"" << host << "\"," << port;

    if (send_at_command(ss.str(), "CONNECT", 5000) || send_at_command("", "OK", 100)) {
        active_links_[link_id] = true;
        return link_id;
    }

    return std::nullopt;
}

bool ESP01SocketClientServer::send_data(int link_id, const uint8_t* data, size_t length) {
    if (link_id < 0 || link_id >= 5 || !active_links_[link_id] || data == nullptr || length == 0) {
        return false;
    }

    std::ostringstream ss;
    ss << "AT+CIPSEND=" << link_id << "," << length;
    if (!send_at_command(ss.str(), ">", 1000)) {
        return false;
    }

    uart_.write_bytes(data, length);
    return send_at_command("", "SEND OK", 3000);
}

bool ESP01SocketClientServer::close_link(int link_id) {
    if (link_id < 0 || link_id >= 5) {
        return false;
    }
    std::ostringstream ss;
    ss << "AT+CIPCLOSE=" << link_id;
    bool res = send_at_command(ss.str(), "OK", 1000);
    active_links_[link_id] = false;
    rx_buffer_.clear_link(link_id);
    return res;
}

bool ESP01SocketClientServer::is_link_active(int link_id) const {
    if (link_id < 0 || link_id >= 5) {
        return false;
    }
    return active_links_[link_id];
}

std::optional<SocketPacket> ESP01SocketClientServer::read_packet() {
    return rx_buffer_.pop_packet();
}

void ESP01SocketClientServer::poll() {
    uint8_t buffer[256];
    size_t count = uart_.read_bytes(buffer, sizeof(buffer));

    for (size_t i = 0; i < count; ++i) {
        process_rx_char(static_cast<char>(buffer[i]));
    }
}

void ESP01SocketClientServer::process_rx_char(char ch) {
    if (parser_state_ == RxState::ReadingIpdPayload) {
        current_ipd_payload_.push_back(static_cast<uint8_t>(ch));
        current_ipd_received_++;
        if (current_ipd_received_ >= current_ipd_expected_) {
            rx_buffer_.append(current_ipd_link_, current_ipd_payload_.data(), current_ipd_payload_.size());
            current_ipd_payload_.clear();
            parser_state_ = RxState::Idle;
        }
        return;
    }

    if (ch == '\r') {
        return;
    }

    if (ch == '\n') {
        if (!rx_line_buffer_.empty()) {
            process_completed_line(rx_line_buffer_);
            rx_line_buffer_.clear();
        }
        return;
    }

    rx_line_buffer_.push_back(ch);
}

void ESP01SocketClientServer::process_completed_line(std::string_view line) {
    // Перевірка події розриву з'єднання: "<id>,CLOSED"
    if (line.find(",CLOSED") != std::string_view::npos) {
        int link_id = line[0] - '0';
        if (link_id >= 0 && link_id < 5) {
            active_links_[link_id] = false;
            rx_buffer_.clear_link(link_id);
        }
        return;
    }

    // Перевірка події підключення клієнта: "<id>,CONNECT"
    if (line.find(",CONNECT") != std::string_view::npos) {
        int link_id = line[0] - '0';
        if (link_id >= 0 && link_id < 5) {
            active_links_[link_id] = true;
        }
        return;
    }

    // Перевірка початку пакунка +IPD: "+IPD,<id>,<len>:"
    if (line.rfind("+IPD,", 0) == 0) {
        size_t comma1 = 5;
        size_t comma2 = line.find(',', comma1);
        size_t colon = line.find(':', comma2);

        if (comma2 != std::string_view::npos && colon != std::string_view::npos) {
            std::string link_str(line.substr(comma1, comma2 - comma1));
            std::string len_str(line.substr(comma2 + 1, colon - comma2 - 1));

            current_ipd_link_ = std::stoi(link_str);
            current_ipd_expected_ = static_cast<size_t>(std::stoul(len_str));
            current_ipd_received_ = 0;
            current_ipd_payload_.clear();
            current_ipd_payload_.reserve(current_ipd_expected_);

            if (current_ipd_expected_ > 0) {
                parser_state_ = RxState::ReadingIpdPayload;
            }
        }
    }
}

bool ESP01SocketClientServer::send_at_command(std::string_view cmd, std::string_view expected_reply, uint32_t timeout_ms) {
    if (!cmd.empty()) {
        std::string full_cmd = std::string(cmd) + "\r\n";
        uart_.write_bytes(reinterpret_cast<const uint8_t*>(full_cmd.data()), full_cmd.size());
    }

    auto start_time = std::chrono::steady_clock::now();
    std::string response;

    while (true) {
        uint8_t buf[64];
        size_t read_bytes = uart_.read_bytes(buf, sizeof(buf));
        if (read_bytes > 0) {
            for (size_t i = 0; i < read_bytes; ++i) {
                char c = static_cast<char>(buf[i]);
                response.push_back(c);
                if (response.find(expected_reply) != std::string::npos) {
                    return true;
                }
                if (response.find("ERROR") != std::string::npos || response.find("FAIL") != std::string::npos) {
                    return false;
                }
            }
        }

        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - start_time).count();
        if (elapsed > timeout_ms) {
            break;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }

    return response.find(expected_reply) != std::string::npos;
}
