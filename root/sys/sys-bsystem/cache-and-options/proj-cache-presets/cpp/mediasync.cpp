// src/mediasync.cpp — ідіоматична реалізація мовою C++20
#include "mediasync_config.h"
#include <iostream>
#include <memory>
#include <string_view>
#include <concepts>
#include <span>

namespace mediasync {

enum class TransportProtocol {
    Quic,
    Tcp,
    UnixSocket
};

[[nodiscard]] constexpr TransportProtocol parse_backend_string(std::string_view name) noexcept {
    if (name == "TCP") return TransportProtocol::Tcp;
    if (name == "UNIX_SOCKET") return TransportProtocol::UnixSocket;
    return TransportProtocol::Quic;
}

struct EngineSettings {
    std::size_t buffer_capacity{MEDIASYNC_BUFFER_SIZE};
    int metrics_port{MEDIASYNC_DEFAULT_PORT};
    std::string_view backend_raw{MEDIASYNC_NETWORK_BACKEND};
    TransportProtocol protocol{parse_backend_string(MEDIASYNC_NETWORK_BACKEND)};
    bool vaapi_active{
#ifdef MEDIASYNC_USE_VAAPI
        true
#else
        false
#endif
    };
};

class MediaSyncPipeline {
public:
    explicit MediaSyncPipeline(EngineSettings settings = {}) 
        : settings_{settings} {
#ifdef MEDIASYNC_ENABLE_LOGGING
        std::cout << "[mediasync-C++] Ініціалізація ядра v" << MEDIASYNC_VERSION_STRING
                  << "\n  • Мережевий бекенд : " << settings_.backend_raw
                  << "\n  • Ємність буфера   : " << settings_.buffer_capacity << " байтів"
                  << "\n  • Порт телеметрії  : " << settings_.metrics_port
                  << "\n  • Апаратний кодек  : " << (settings_.vaapi_active ? "VA-API (активовано)" : "Програмний")
                  << std::endl;
#endif
    }

    [[nodiscard]] std::string_view backend_name() const noexcept {
        return settings_.backend_raw;
    }

    [[nodiscard]] bool is_hardware_accelerated() const noexcept {
        return settings_.vaapi_active;
    }

private:
    EngineSettings settings_;
};

} // namespace mediasync
