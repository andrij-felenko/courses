/* Стенд: те саме розділення контекстів, що й у прошивці, але замість
   переривання таймера — цикл по модельному часу, а замість GPIO — сценарій
   натискань із брязкотом. Політики пінів підставляють модель замість
   регістрів периферії, і жодного рядка бібліотеки міняти не треба. */

#include <array>
#include <cstdint>
#include <iomanip>
#include <iostream>

#include "button.hpp"
#include "event_queue.hpp"
#include "input_event.hpp"
#include "rotary_encoder.hpp"

namespace {

using namespace input;

constexpr Millis Tick{5};
constexpr std::uint32_t RunMs = 6000;
constexpr std::uint32_t BounceMs = 8;     // скільки брязкотить контакт кнопки
constexpr std::uint32_t EncBounceMs = 4;  // скільки брязкотить фаза енкодера

std::uint32_t g_nowMs = 0;

struct Press {
    std::uint32_t downMs;
    std::uint32_t upMs;
};

constexpr std::array<Press, 4> kPresses{{
    {  100,  180 },  // короткий клік
    {  600,  680 },  // перше натискання пари
    {  780,  860 },  // друге — має дати DoubleClick
    { 1500, 5200 },  // довге утримання: Start, Hold і автоповтор із розгоном
}};

/* Свій LCG, а не rand(): прогін мусить бути повторюваним, інакше
   «воно іноді ламається» не відтвориш. */
std::uint32_t g_rnd = 12345;

bool noisyBit() noexcept {
    g_rnd = g_rnd * 1103515245u + 12345u;
    return ((g_rnd >> 20) & 1u) != 0;
}

/* Політика піна кнопки. Active-low ховається саме тут: назовні — чесне
   «натиснуто чи ні». Протягом BounceMs після фронту віддаємо випадковий
   рівень — це і є брязкіт, через який наївний лічильник у перериванні
   наростає на 7 за одне натискання. */
struct ButtonPin {
    static bool isPressed() noexcept {
        for (const Press& p : kPresses) {
            if (g_nowMs >= p.downMs && g_nowMs < p.upMs) {
                return (g_nowMs < p.downMs + BounceMs) ? noisyBit() : true;
            }
            if (g_nowMs >= p.upMs && g_nowMs < p.upMs + BounceMs) {
                return noisyBit();
            }
        }
        return false;
    }
};

/* Модель валу: чверть періоду за 10 мс. */
std::int32_t encoderPosition(std::uint32_t t) noexcept {
    std::int32_t pos = 0;
    if (t > 2400) {  // за годинниковою
        pos += static_cast<std::int32_t>(((t < 3200 ? t : 3200) - 2400) / 10);
    }
    if (t > 4000) {  // назад
        pos -= static_cast<std::int32_t>(((t < 4400 ? t : 4400) - 4000) / 10);
    }
    return pos;
}

/* Код Грея на двох бітах: 00 → 01 → 11 → 10 → 00 при русі вперед. */
std::uint8_t grayAt(std::uint32_t t) noexcept {
    const std::uint32_t n = static_cast<std::uint32_t>(encoderPosition(t) + 4096) & 3u;
    return static_cast<std::uint8_t>(n ^ (n >> 1));
}

template <int Bit>
bool phaseAt(std::uint32_t t) noexcept {
    const std::uint8_t gray = grayAt(t);
    return ((gray >> Bit) & 1u) != 0;
}

/* Брязкотить лише та фаза, що саме перемикається: механічно друга в цей
   момент розімкнена намертво. Тому заборонених переходів стенд не породжує —
   вони бувають на живому валу, і лічильник glitches() чекає саме на них. */
template <int Bit>
bool readPhase() noexcept {
    const std::uint32_t back = (g_nowMs >= EncBounceMs) ? g_nowMs - EncBounceMs : 0;
    const bool now = phaseAt<Bit>(g_nowMs);
    return (now != phaseAt<Bit>(back)) ? noisyBit() : now;
}

struct PhaseAPin {
    static bool isHigh() noexcept { return readPhase<1>(); }
};

struct PhaseBPin {
    static bool isHigh() noexcept { return readPhase<0>(); }
};

}  // namespace

int main() {
    /* Уся пам'ять статична: ні new, ні фрагментації, ні сюрпризів на
       мікроконтролері з двома кілобайтами SRAM. */
    static EventQueue<InputEvent, 16> queue;
    static Button<ButtonPin> button{1};
    static RotaryEncoder<PhaseAPin, PhaseBPin> encoder{2};

    for (g_nowMs = 0; g_nowMs <= RunMs; g_nowMs += Tick.count()) {
        // Контекст переривання таймера: лише вибірка, автомат і черга.
        button.tick(Tick, queue);
        encoder.tick(queue);

        // Контекст головного циклу: тут уже можна працювати повільно.
        if (g_nowMs == 1000) {
            std::cout << std::setw(6) << g_nowMs << " мс  зміна екрана: відкидаємо "
                      << queue.size() << " подій\n";
            queue.clear();
            continue;
        }

        while (const std::optional<InputEvent> evt = queue.pop()) {
            std::cout << std::setw(6) << g_nowMs << " мс  id=" << unsigned{evt->id}
                      << "  " << std::left << std::setw(16) << name(evt->type)
                      << std::right << "  " << evt->durationMs << " мс\n";
        }
    }

    if (const std::uint32_t dropped = queue.dropped(); dropped != 0) {
        std::cout << "черга переповнювалася: втрачено " << dropped << " подій\n";
    }
    std::cout << "заборонених переходів енкодера: " << encoder.glitches() << '\n';
    return 0;
}
