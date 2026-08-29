/*
 * Стенд приймача: збираємо кадри збоку відправника й пропускаємо їх через
 * SecureChannel::parse(), перевіряючи, що конвеєр відповідає саме тим
 * статусом, якого чекає протокол.
 */
#include <algorithm>
#include <array>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <span>
#include <string>
#include <string_view>
#include <variant>

#include "secure_frame.hpp"

namespace {

int failures = 0;

void check(std::string_view name, bool ok, std::string_view detail = {}) {
    std::cout << std::left << std::setw(46) << name
              << (ok ? "[ ok ]" : "[FAIL]") << "  " << detail << '\n';
    if (!ok) {
        ++failures;
    }
}

/* ---- бік відправника: серіалізація кадру ------------------------------- */

template <typename T>
void store_le(std::span<std::uint8_t> out, T value) noexcept {
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        out[i] = static_cast<std::uint8_t>(static_cast<std::uint64_t>(value) >> (8U * i));
    }
}

/* Повертає готовий кадр або порожній span, якщо буфер замалий. */
std::span<std::uint8_t> build_frame(std::span<std::uint8_t> buf,
                                    std::uint8_t type,
                                    std::uint64_t seq,
                                    std::uint32_t timestamp,
                                    std::span<const std::uint8_t> payload,
                                    std::span<const std::uint8_t> key) {
    const std::size_t signed_len = secure::kHeaderSize + payload.size();
    const std::size_t total      = signed_len + secure::kTagSize;
    if (total > buf.size()) {
        return {};
    }

    store_le<std::uint16_t>(buf, secure::kFrameMagic);
    buf[2] = type;
    buf[3] = 0;                                   /* reserved */
    store_le<std::uint64_t>(buf.subspan(4), seq);
    store_le<std::uint32_t>(buf.subspan(12), timestamp);
    store_le<std::uint16_t>(buf.subspan(16), static_cast<std::uint16_t>(payload.size()));
    std::copy(payload.begin(), payload.end(),
              buf.begin() + static_cast<std::ptrdiff_t>(secure::kHeaderSize));

    const auto tag = secure::hmac_sha256(key, buf.first(signed_len));
    std::copy(tag.begin(), tag.end(), buf.begin() + static_cast<std::ptrdiff_t>(signed_len));
    return buf.first(total);
}

/* ---- самоперевірка криптографії --------------------------------------- */

std::string to_hex(std::span<const std::uint8_t> bytes) {
    static constexpr std::string_view kDigits = "0123456789abcdef";
    std::string out;
    out.reserve(bytes.size() * 2);
    for (auto b : bytes) {
        out.push_back(kDigits[b >> 4]);
        out.push_back(kDigits[b & 0x0FU]);
    }
    return out;
}

std::span<const std::uint8_t> as_bytes_of(std::string_view text) noexcept {
    return {reinterpret_cast<const std::uint8_t*>(text.data()), text.size()};
}

/*
 * Без цієї перевірки решта стенда безглузда: конвеєр однаково "працював би"
 * і з підробленим хешем, який завжди повертає нулі. Вектори — з FIPS 180-4
 * (SHA-256 від "abc") і RFC 4231, тест 2 (HMAC з ключем "Jefe").
 */
void crypto_self_test() {
    const auto digest = secure::Sha256::hash(as_bytes_of("abc"));
    check("SHA-256(\"abc\") = вектор FIPS 180-4",
          to_hex(digest) == "ba7816bf8f01cfea414140de5dae2223"
                            "b00361a396177a9cb410ff61f20015ad");

    const auto tag = secure::hmac_sha256(as_bytes_of("Jefe"),
                                         as_bytes_of("what do ya want for nothing?"));
    check("HMAC-SHA256 = вектор RFC 4231 #2",
          to_hex(tag) == "5bdcc146bf60754e6a042426089575c7"
                         "5a003f089d2739839dec58b964ec3843");
}

constexpr std::uint8_t kMsgSetServoAngle = 0x01;

}  // namespace

int main() {
    using namespace secure;

    static constexpr std::array<std::uint8_t, 16> key{
        'm', 'c', 'u', '_', 's', 'e', 'c', 'r', 'e', 't', '_', 'k', 'e', 'y', '_', '1'
    };
    constexpr std::array<std::uint8_t, 2> payload{0x00, 0x5A};   /* кут 90 градусів */
    constexpr std::uint32_t base_time = 1700000000U;

    crypto_self_test();

    SecureChannel channel{key, /* max_drift_s = */ 10U};
    std::array<std::uint8_t, 64> buffer{};

    /* 1. Легітимний кадр: вікно порожнє, лічильник 100. */
    auto frame = build_frame(buffer, kMsgSetServoAngle, 100, base_time, payload, key);
    auto result = channel.parse(frame, base_time + 5U);
    const auto* command = std::get_if<Command>(&result);
    check("1. Легітимний кадр (seq=100)",
          command != nullptr && command->type == kMsgSetServoAngle
              && command->payload.size() == 2 && command->payload[1] == 0x5A,
          command != nullptr ? "кут " + std::to_string(command->payload[1])
                             : std::string{to_string(std::get<ParseError>(result))});

    /* 2. Атака повтору: той самий байт у байт кадр удруге. Тег правильний —
     *    відсікає саме вікно, а не криптографія. */
    result = channel.parse(frame, base_time + 6U);
    const auto* error = std::get_if<ParseError>(&result);
    check("2. Повтор того самого кадру",
          error != nullptr && *error == ParseError::ReplayDetected,
          error != nullptr ? std::string{to_string(*error)} : "кадр пройшов!");

    /* 3. Підміна навантаження: кадр із новим лічильником 101, у якому
     *    зловмисник перевернув один біт кута. Тег більше не сходиться. */
    frame = build_frame(buffer, kMsgSetServoAngle, 101, base_time, payload, key);
    frame[kHeaderSize + 1] ^= 0x01U;                          /* 90 градусів -> 91 */
    const std::uint64_t max_before = channel.window().max_sequence();
    result = channel.parse(frame, base_time + 7U);
    error = std::get_if<ParseError>(&result);
    /* Вікно не зсунулося: підроблений кадр не витратив лічильник 101. */
    check("3. Змінений біт у навантаженні",
          error != nullptr && *error == ParseError::AuthFailed
              && channel.window().max_sequence() == max_before,
          "max_seq " + std::to_string(max_before) + " -> "
              + std::to_string(channel.window().max_sequence()));

    /* 4. Запізнілий кадр у межах вікна: радіо переставило пакети місцями. */
    frame = build_frame(buffer, kMsgSetServoAngle, 95, base_time, payload, key);
    result = channel.parse(frame, base_time + 8U);
    check("4. Запізнілий кадр у вікні (seq=95)",
          std::holds_alternative<Command>(result),
          "max_seq лишається " + std::to_string(channel.window().max_sequence()));

    /* 5. Кадр із-за краю вікна: лічильник на 65 менший за максимум.
     *    Тег правильний, але памʼяті про нього вже немає — відкидаємо. */
    frame = build_frame(buffer, kMsgSetServoAngle, 100 - 65, base_time, payload, key);
    result = channel.parse(frame, base_time + 9U);
    error = std::get_if<ParseError>(&result);
    check("5. Застарілий кадр поза вікном (seq=35)",
          error != nullptr && *error == ParseError::ReplayDetected,
          error != nullptr ? std::string{to_string(*error)} : "кадр пройшов!");

    std::cout << '\n'
              << (failures == 0 ? "усі перевірки пройдено" : "Є ПРОВАЛЕНІ ПЕРЕВІРКИ")
              << '\n';
    return failures == 0 ? 0 : 1;
}
