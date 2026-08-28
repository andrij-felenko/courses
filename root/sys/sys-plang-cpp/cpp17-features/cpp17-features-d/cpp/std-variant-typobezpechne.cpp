#include <variant>

struct KeyPress { int key_code; };
struct MouseClick { int x, y; };
struct WindowResize { int width, height; };

using Event = std::variant<KeyPress, MouseClick, WindowResize>;

void dispatch_event(const Event& event) {
    std::visit([](const auto& e) {
        using T = std::decay_t<decltype(e)>;
        if constexpr (std::is_same_v<T, KeyPress>) {
            std::cout << "Натиснуто клавішу: " << e.key_code << "\n";
        } else if constexpr (std::is_same_v<T, MouseClick>) {
            std::cout << "Клік миші: " << e.x << ", " << e.y << "\n";
        } else if constexpr (std::is_same_v<T, WindowResize>) {
            std::cout << "Зміна розміру: " << e.width << "x" << e.height << "\n";
        }
    }, event);
}
