#pragma once

#include <utility>

#include "esp_http_server.h"

#include "portal/esp_result.hpp"

namespace portal::http {

/*
 * Вбудований веб-сервер порталу: сторінка майстра з Flash, REST-обробники
 * сканування й збереження та універсальний перехоплювач, що відповідає
 * 302-м на будь-який невідомий шлях.
 *
 * Об'єкт володіє дескриптором сервера: сокети звільняються в деструкторі.
 */
class Server {
public:
    Server() noexcept = default;

    Server(const Server &) = delete;
    Server &operator=(const Server &) = delete;

    Server(Server &&other) noexcept : handle_{std::exchange(other.handle_, nullptr)} {}

    Server &operator=(Server &&other) noexcept
    {
        if (this != &other) {
            stop();
            handle_ = std::exchange(other.handle_, nullptr);
        }
        return *this;
    }

    ~Server() { stop(); }

    [[nodiscard]] Status start() noexcept;

    void stop() noexcept;

    [[nodiscard]] bool running() const noexcept { return handle_ != nullptr; }

private:
    httpd_handle_t handle_{nullptr};
};

}  // namespace portal::http
