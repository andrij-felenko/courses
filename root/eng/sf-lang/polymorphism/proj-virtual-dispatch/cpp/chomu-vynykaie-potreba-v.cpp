#include <cstddef>
#include <cstdint>
#include <span>

struct IDrawableVTable {
    void (*draw)(void* self) noexcept;
};

struct IDrawable {
    const IDrawableVTable* vptr{nullptr};
};

struct ISerializableVTable {
    void (*serialize)(void* self, std::span<uint8_t> out) noexcept;
};

struct ISerializable {
    const ISerializableVTable* vptr{nullptr};
};

/* Складений клас із двома незалежними vptr */
struct Button {
    IDrawable drawable_base;
    ISerializable serializable_base;
    int width{0};
    int height{0};

    void actual_draw() noexcept {
        /* Логіка малювання кнопки */
    }

    void actual_serialize(std::span<uint8_t> out) noexcept {
        /* Логіка серіалізації кнопки */
        (void)out;
    }

    Button(int w, int h) noexcept : width(w), height(h) {
        static constexpr IDrawableVTable draw_vtbl{
            .draw = [](void* self) noexcept {
                auto* b = static_cast<Button*>(self);
                b->actual_draw();
            }
        };

        static constexpr ISerializableVTable ser_vtbl{
            .serialize = [](void* self, std::span<uint8_t> out) noexcept {
                auto* bytes = static_cast<uint8_t*>(self);
                auto* b = reinterpret_cast<Button*>(bytes - offsetof(Button, serializable_base));
                b->actual_serialize(out);
            }
        };

        drawable_base.vptr = &draw_vtbl;
        serializable_base.vptr = &ser_vtbl;
    }
};
