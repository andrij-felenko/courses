#include "secure_frame.hpp"

namespace secure {
namespace {

/*
 * Поля читаємо побайтово, а не накладанням структури на буфер.
 *
 * Дві причини, і обидві коштують прошивці життя. Перша: буфер приїхав з DMA
 * і лежить за довільною адресою, а на Cortex-M0 звернення до 64-бітного
 * лічильника за невирівняною адресою — це HardFault, тобто перезавантаження
 * контролера з пульта зловмисника. Друга: порядок байтів у кадрі заданий
 * протоколом (молодший перший), а не тим, на якому ядрі зібрали прошивку.
 */
template <typename T>
[[nodiscard]] T load_le(std::span<const std::uint8_t> bytes) noexcept {
    std::uint64_t value = 0;
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        value |= static_cast<std::uint64_t>(bytes[i]) << (8U * i);
    }
    return static_cast<T>(value);
}

/*
 * Порівняння за фіксовану кількість тактів. Звичайне std::equal виходить на
 * першому розбіжному байті, і різниця в часі відповіді дає зловмиснику
 * підбирати тег побайтово: 32·256 спроб замість 2^256.
 */
[[nodiscard]] bool constant_time_equal(std::span<const std::uint8_t> a,
                                       std::span<const std::uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;                   /* довжина не секрет — її знає протокол */
    }
    volatile std::uint8_t diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        diff = static_cast<std::uint8_t>(diff | (a[i] ^ b[i]));
    }
    return diff == 0;
}

}  // namespace

std::string_view to_string(ParseError error) noexcept {
    switch (error) {
    case ParseError::BufferTooSmall:   return "BufferTooSmall";
    case ParseError::InvalidMagic:     return "InvalidMagic";
    case ParseError::PayloadMismatch:  return "PayloadMismatch";
    case ParseError::AuthFailed:       return "AuthFailed";
    case ParseError::TimestampExpired: return "TimestampExpired";
    case ParseError::ReplayDetected:   return "ReplayDetected";
    }
    return "Unknown";
}

ParseResult SecureChannel::parse(std::span<const std::uint8_t> frame,
                                 std::uint32_t now_s) noexcept {
    /* 0. Рамка. Поки в буфері немає навіть заголовка з тегом, читати нічого. */
    if (frame.size() < kFrameOverhead) {
        return ParseError::BufferTooSmall;
    }

    if (load_le<std::uint16_t>(frame) != kFrameMagic) {
        return ParseError::InvalidMagic;
    }

    const auto payload_len = load_le<std::uint16_t>(frame.subspan(16));
    const std::size_t signed_len = kHeaderSize + payload_len;
    const std::size_t total_len  = signed_len + kTagSize;

    /* Оголошена довжина мусить уміщатися в те, що справді прийшло. Буфер
     * може бути й довшим (DMA віддає його блоком фіксованого розміру) —
     * зайвий хвіст просто не входить у кадр і під підпис не потрапляє. */
    if (total_len > frame.size()) {
        return ParseError::PayloadMismatch;
    }

    /* 1. Автентифікація ПЕРШОЮ. Досі ми не торкалися жодного поля корисного
     *    навантаження — тільки рамки, потрібної, щоб знайти тег. */
    const Sha256::Digest computed = hmac_sha256(key_, frame.first(signed_len));
    if (!constant_time_equal(frame.subspan(signed_len, kTagSize), computed)) {
        return ParseError::AuthFailed;
    }

    /* Далі поля вже підписані відправником — їм можна вірити. */
    const auto seq       = load_le<std::uint64_t>(frame.subspan(4));
    const auto timestamp = load_le<std::uint32_t>(frame.subspan(12));

    /* 2. Часові межі. Підписаний, але дворічної давнини кадр — так само
     *    атака повтору, просто на канал, де вікно вже зсунулося. */
    const std::uint32_t drift = (now_s >= timestamp) ? (now_s - timestamp)
                                                     : (timestamp - now_s);
    if (drift > max_drift_s_) {
        return ParseError::TimestampExpired;
    }

    /* 3. Ковзне вікно: дублікат чи безнадійно застарілий лічильник. */
    if (!window_.check(seq)) {
        return ParseError::ReplayDetected;
    }

    /* 4. Стан рухаємо лише тепер, коли кадр пройшов усі перевірки. */
    window_.commit(seq);

    /* 5. Віддаємо команду диспетчеру: навантаження без копіювання. */
    return Command{
        .type      = frame[2],
        .seq       = seq,
        .timestamp = timestamp,
        .payload   = frame.subspan(kHeaderSize, payload_len)
    };
}

}  // namespace secure
