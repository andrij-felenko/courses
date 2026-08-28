// Доступ до вбудованого ресурсу з використанням std::span та std::string_view (C++)
#include <iostream>
#include <span>
#include <string_view>
#include <cstdint>

extern "C" {
    extern const uint8_t _binary_server_root_cert_pem_start[];
    extern const uint8_t _binary_server_root_cert_pem_end[];
}

void display_certificate_info() {
    const auto* start = reinterpret_cast<const char*>(_binary_server_root_cert_pem_start);
    const auto* end = reinterpret_cast<const char*>(_binary_server_root_cert_pem_end);
    const std::string_view cert_view(start, static_cast<size_t>(end - start));

    std::cout << "Вбудований сертифікат (C++ span): " << cert_view.size() << " байтів\n";
}
