#include "telemetry.hpp"

#include <array>
#include <avr/interrupt.h>
#include <avr/io.h>
#include <util/atomic.h>

namespace gimbal::telemetry {
namespace {

constexpr std::uint8_t kBufSize = 128;  // степінь двійки: маска замість ділення
constexpr std::uint8_t kBufMask = kBufSize - 1;

// Тут саме сирий масив, а не std::array: у std::array немає volatile-версії
// operator[], і кільце, яке ділять контур і переривання, з ним не збереш.
volatile std::uint8_t  g_buf[kBufSize]{};
volatile std::uint8_t  g_head = 0;   // куди пише контур
volatile std::uint8_t  g_tail = 0;   // звідки бере переривання
volatile std::uint16_t g_dropped = 0;

void put(char c) noexcept {
    const std::uint8_t next = static_cast<std::uint8_t>((g_head + 1) & kBufMask);

    if (next == g_tail) {
        ++g_dropped;  // кільце повне: губимо байт, але не такт
        return;
    }

    g_buf[g_head] = static_cast<std::uint8_t>(c);
    g_head = next;

    // Дозвіл переривання — атомарно: інакше ISR устигне побачити порожнє
    // кільце між записом байта й увімкненням передавача.
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        UCSR0B |= (1 << UDRIE0);
    }
}

}  // namespace

void begin(std::uint32_t baud) noexcept {
    // Подвійна швидкість дає меншу похибку ділення на 16 МГц:
    // для 115200 це 2.1% замість 3.5%, і приймач на боці ПК не збивається.
    const auto ubrr = static_cast<std::uint16_t>((F_CPU / (8UL * baud)) - 1UL);

    UBRR0H = static_cast<std::uint8_t>(ubrr >> 8);
    UBRR0L = static_cast<std::uint8_t>(ubrr);

    UCSR0A = (1 << U2X0);
    UCSR0B = (1 << TXEN0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);  // 8N1

    g_head = g_tail = 0;
    g_dropped = 0;
}

void write(std::string_view text) noexcept {
    // string_view несе довжину із собою — жодного пошуку нуля й жодної
    // пари «вказівник плюс окремий аргумент довжини», яку можна розсинхронити.
    for (char c : text) {
        put(c);
    }
}

void write(std::int32_t value) noexcept {
    std::array<char, 11> digits{};
    std::uint8_t         n = 0;
    std::uint32_t        u = 0;

    if (value < 0) {
        put('-');
        u = static_cast<std::uint32_t>(-(value + 1)) + 1u;  // обхід INT32_MIN
    } else {
        u = static_cast<std::uint32_t>(value);
    }

    do {
        digits[n++] = static_cast<char>('0' + (u % 10u));
        u /= 10u;
    } while (u != 0u);

    while (n != 0) {
        put(digits[--n]);
    }
}

std::uint16_t dropped() noexcept {
    std::uint16_t v = 0;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        v = g_dropped;
    }
    return v;
}

}  // namespace gimbal::telemetry

ISR(USART_UDRE_vect) {
    using namespace gimbal::telemetry;

    if (g_head == g_tail) {
        // Кільце порожнє — глушимо переривання, інакше воно крутитиметься
        // безперервно й з'їсть увесь запас часу такту.
        UCSR0B &= static_cast<std::uint8_t>(~(1 << UDRIE0));
        return;
    }

    UDR0 = g_buf[g_tail];
    g_tail = static_cast<std::uint8_t>((g_tail + 1) & kBufMask);
}
