#include <string_view>

struct DeviceDescriptor {
    int port;
    int baud_rate;
    bool is_active;

    // Конструктор повинен підтримувати constexpr
    constexpr DeviceDescriptor(int p, int baud)
        : port(p), baud_rate(baud), is_active(false) {}
};

// C++20 constinit: змінна є МУТАБЕЛЬНОЮ (не const),
// але гарантовано ініціалізується у статичній фазі:
constinit DeviceDescriptor g_primary_device(8080, 115200);

void enable_device() {
    // Зміну стану дозволено під час виконання!
    g_primary_device.is_active = true;
}
