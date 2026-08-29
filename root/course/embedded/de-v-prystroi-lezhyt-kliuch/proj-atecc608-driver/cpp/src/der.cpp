#include "der.hpp"

namespace atecc {
namespace {

// Чип віддає R і S як 32 байти з ведучими нулями, а DER вимагає цілого зі
// знаком у мінімальній формі: нулі спереду зрізаємо, але якщо старший біт
// лишився одиницею — дописуємо нульовий байт, інакше число стане від'ємним.
void appendInteger(std::vector<std::uint8_t>& out, std::span<const std::uint8_t> value)
{
    while (value.size() > 1 && value.front() == 0x00) {
        value = value.subspan(1);
    }
    const bool pad = (value.front() & 0x80) != 0;

    out.push_back(0x02); // тег INTEGER
    out.push_back(static_cast<std::uint8_t>(value.size() + (pad ? 1 : 0)));
    if (pad) {
        out.push_back(0x00);
    }
    out.insert(out.end(), value.begin(), value.end());
}

} // namespace

std::vector<std::uint8_t> encodeDerSignature(std::span<const std::uint8_t, kSignatureSize> raw)
{
    std::vector<std::uint8_t> body;
    body.reserve(70);
    appendInteger(body, raw.first(32));  // R
    appendInteger(body, raw.last(32));   // S

    std::vector<std::uint8_t> der;
    der.reserve(body.size() + 2);
    der.push_back(0x30);                                  // тег SEQUENCE
    der.push_back(static_cast<std::uint8_t>(body.size())); // тіло не сягає 128 байтів
    der.insert(der.end(), body.begin(), body.end());
    return der;
}

} // namespace atecc
