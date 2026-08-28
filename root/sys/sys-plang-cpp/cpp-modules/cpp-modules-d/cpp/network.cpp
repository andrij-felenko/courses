// Файл: network.cpp
module network;

#include <sys/socket.h>
#include <unistd.h>

namespace net {

TcpSocket::TcpSocket() = default;

TcpSocket::~TcpSocket() {
    if (m_native_handle >= 0) {
        ::close(m_native_handle);
    }
}

void TcpSocket::connect(const char* host, int port) {
    // Низькорівневий виклик операційної системи
}

void TcpSocket::send(const char* data, int len) {
    // Логіка відправлення мережевих пакетів
}

} // namespace net
