// C++: Ідіоматичний неблокуючий обробник робіт
#include <span>
#include <array>

class SensorWorkItem {
public:
    struct Context {
        std::array<uint8_t, 8> buffer{};
        bool ready{false};
    };

    static void execute(void* raw_context) noexcept {
        if (!raw_context) return;
        auto* ctx = static_cast<Context*>(raw_context);

        // Перевірка стану та швидке неблокуюче оновлення контексту
        ctx->buffer.fill(0x55);
        ctx->ready = true;
    }
};
