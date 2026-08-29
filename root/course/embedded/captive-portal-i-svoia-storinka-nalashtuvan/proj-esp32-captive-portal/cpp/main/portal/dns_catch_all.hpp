#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "portal/esp_result.hpp"
#include "portal/unique_socket.hpp"

namespace portal::dns {

/*
 * Catch-all DNS: окреме завдання FreeRTOS слухає UDP-порт 53 і на будь-який
 * запит типу A відповідає адресою точки доступу.
 *
 * Саме ця підміна й змушує телефон побачити «підозрілу» мережу: його зонд
 * стукає до відомого імені, отримує адресу мікроконтролера, бачить не той
 * вміст і показує сторінку входу.
 */
class CatchAllServer {
public:
    static constexpr std::uint16_t kPort = 53;

    /*
     * 512 байтів — історична межа DNS поверх UDP. Буфер лежить на стеку
     * завдання: купу не чіпаємо взагалі, тож потік запитів від фонових
     * служб телефона не фрагментує пам'ять.
     */
    static constexpr std::size_t kBufferSize = 512;

    /*
     * 3072 байти стеку: 512 з них з'їдає буфер пакета, решта йде на
     * внутрішні структури сокетів LWIP і кадри викликів.
     */
    static constexpr std::uint32_t kTaskStack = 3072;
    static constexpr UBaseType_t kTaskPriority = 5;

    /* answerIp — адреса у мережевому порядку байтів (esp_ip4addr_aton). */
    explicit CatchAllServer(std::uint32_t answerIp) noexcept : answerIp_{answerIp} {}

    CatchAllServer(const CatchAllServer &) = delete;
    CatchAllServer &operator=(const CatchAllServer &) = delete;

    ~CatchAllServer() { stop(); }

    [[nodiscard]] Status start() noexcept;

    /* Зупиняє завдання й закриває сокет; повертається після виходу завдання. */
    void stop() noexcept;

    [[nodiscard]] bool running() const noexcept { return running_.load(); }

private:
    static void taskEntry(void *context) noexcept;

    void serve() noexcept;

    UniqueSocket socket_;
    TaskHandle_t task_{nullptr};
    std::atomic<bool> running_{false};
    std::uint32_t answerIp_{};
};

}  // namespace portal::dns
