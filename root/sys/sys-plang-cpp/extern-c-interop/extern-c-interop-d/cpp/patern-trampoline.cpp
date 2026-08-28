#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <cstdint>

/* Оголошення зовнішнього C-API */
extern "C" {
    typedef void (*data_ready_cb)(const uint8_t* data, size_t len, void* user_data);
    void stream_register_handler(data_ready_cb cb, void* user_data);
}

// C++ клас-обробник подій
class NetworkReceiver {
public:
    void handle_chunk(std::span<const uint8_t> buffer) {
        bytes_accumulated_ += buffer.size();
        std::cout << "[C++ Handler] Отримано чанк: " << buffer.size() 
                  << " байтів (сумарно: " << bytes_accumulated_ << ")\n";
    }

    void subscribe_to_stream() {
        // Статичний трамплін: C calling convention, без захоплення стану
        auto trampoline = [](const uint8_t* data, size_t len, void* user_data) noexcept {
            auto* self = static_cast<NetworkReceiver*>(user_data);
            if (self && data) {
                self->handle_chunk(std::span<const uint8_t>(data, len));
            }
        };

        // Реєстрація: передаємо статичну функцію-трамплін та покажчик this
        stream_register_handler(trampoline, this);
    }

private:
    size_t bytes_accumulated_{0};
};

int main() {
    NetworkReceiver receiver;
    receiver.subscribe_to_stream();
    return 0;
}
