// Так це рахує прошивка: constexpr — тобто ще при компіляції,
// у двійковий образ потрапляє готова стала.
#include <cstdint>

constexpr uint32_t fnv1a32(const char *s, uint32_t h = 0x811c9dc5u)
{
    return *s ? fnv1a32(s + 1, (h ^ static_cast<uint8_t>(*s)) * 0x01000193u) : h;
}

constexpr uint32_t eventId(uint8_t component, const char *name)
{
    return (static_cast<uint32_t>(component) << 24) | (fnv1a32(name) & 0x00FFFFFFu);
}

static_assert(eventId(1, "commander_rtl") == 0x01352ce4u, "");
