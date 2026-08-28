#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>

extern "C" void uart_send_byte_blocking(uint8_t ch);
extern "C" void itm_send_byte(uint8_t ch);

/* C++ обгортка над системним викликом із використанням std::span */
extern "C" int _write(int fd, const char *buf, int len) {
    if ((fd == 1 || fd == 2) && buf != nullptr && len > 0) {
        std::span<const char> data(buf, static_cast<size_t>(len));
        for (const char ch : data) {
            if (ch == '\n') {
                uart_send_byte_blocking(static_cast<uint8_t>('\r'));
            }
            uart_send_byte_blocking(static_cast<uint8_t>(ch));
        }
        return len;
    }
    return -1;
}
