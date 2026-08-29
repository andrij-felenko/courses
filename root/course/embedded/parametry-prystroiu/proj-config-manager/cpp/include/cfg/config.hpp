#pragma once
// config.hpp — розкладка запису у Flash, коди помилок і дрібні операції над нею.
// Структури тут — саме те, що лежить у пам'яті, тож їхній розмір зафіксовано.

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <optional>
#include <span>
#include <string_view>
#include <type_traits>

namespace cfg {

inline constexpr std::uint32_t kMagic         = 0x43464731U;  // "CFG1"
inline constexpr std::uint16_t kSchemaV1      = 1;
inline constexpr std::uint16_t kSchemaV2      = 2;
inline constexpr std::uint16_t kSchemaCurrent = kSchemaV2;

inline constexpr std::size_t   kSectorSize    = 256;
inline constexpr std::uint32_t kTrialTimeoutS = 60;
inline constexpr std::uint32_t kReportMaxS    = 86400;

// Текстове поле фіксованої довжини — так воно лежить у секторі.
template <std::size_t N>
using Text = std::array<char, N>;

template <std::size_t N>
[[nodiscard]] constexpr bool terminated(const Text<N>& field) noexcept
{
    return std::find(field.begin(), field.end(), '\0') != field.end();
}

template <std::size_t N>
[[nodiscard]] constexpr std::string_view view(const Text<N>& field) noexcept
{
    const auto end = std::find(field.begin(), field.end(), '\0');
    return std::string_view{field.data(), static_cast<std::size_t>(end - field.begin())};
}

// Повертає false, якщо рядок не влазить у поле: обрізали — треба знати.
template <std::size_t N>
constexpr bool assign(Text<N>& field, std::string_view text) noexcept
{
    field.fill('\0');
    const std::size_t n = std::min(text.size(), N - 1);
    std::copy_n(text.data(), n, field.data());
    return n == text.size();
}

// Схема v1 — до OTA-оновлення: лише адреса IPv4, без порту, TLS і таймауту.
struct PayloadV1 {
    Text<32> wifi_ssid;
    Text<32> wifi_pass;
    std::array<std::uint8_t, 4> broker_ip;
    std::uint32_t report_interval_s;
};

// Схема v2 — поточна.
struct PayloadV2 {
    Text<32> wifi_ssid;
    Text<32> wifi_pass;
    Text<48> broker_host;
    std::uint16_t broker_port;
    std::uint16_t tls_enable;
    std::uint32_t report_interval_s;
    std::uint32_t conn_timeout_s;
};

// Заголовок запису. Програмується ОСТАННІМ: без магії сектор для читача не існує.
struct Header {
    std::uint32_t magic;
    std::uint16_t schema_version;
    std::uint16_t flags;
    std::uint32_t sequence_number;
    std::uint16_t payload_len;
    std::uint16_t reserved;
    std::uint32_t crc32_value;
};

static_assert(sizeof(Header) == 20, "заголовок не мусить діставати вирівнювання");
static_assert(sizeof(PayloadV1) == 72, "розкладка v1 зафіксована у Flash");
static_assert(sizeof(PayloadV2) == 124, "розкладка v2 зафіксована у Flash");

enum class Error : std::uint8_t {
    NoValidRecord,       // сектор стертий, без магії або з битим CRC
    BadPayloadSize,      // довжина запису не збігається зі схемою
    UnknownSchema,       // запис новіший за прошивку
    FieldNotTerminated,  // текстове поле без завершального нуля
    EmptySsid,
    EmptyHost,
    BadPort,
    TlsFlagInvalid,
    BadInterval,
    TimeoutTooShort,     // таймаут зв'язку не більший за інтервал звітування
    TrialActive,
    NoTrial,
    FlashWriteRejected,  // сектор не взяв програмування
    FlashVerifyFailed,   // записане не збіглося з прочитаним
};

[[nodiscard]] constexpr std::string_view describe(Error e) noexcept
{
    switch (e) {
    case Error::NoValidRecord:      return "придатного запису немає";
    case Error::BadPayloadSize:     return "довжина запису не відповідає схемі";
    case Error::UnknownSchema:      return "невідома версія схеми";
    case Error::FieldNotTerminated: return "текстове поле без завершального нуля";
    case Error::EmptySsid:          return "порожній SSID";
    case Error::EmptyHost:          return "порожня адреса брокера";
    case Error::BadPort:            return "порт брокера дорівнює 0";
    case Error::TlsFlagInvalid:     return "прапорець TLS має бути 0 або 1";
    case Error::BadInterval:        return "інтервал звітування поза межами";
    case Error::TimeoutTooShort:    return "таймаут зв'язку не більший за інтервал звітування";
    case Error::TrialActive:        return "випробування вже триває";
    case Error::NoTrial:            return "немає чого фіксувати";
    case Error::FlashWriteRejected: return "сектор Flash не прийняв запис";
    case Error::FlashVerifyFailed:  return "звірка записаного сектора не пройшла";
    }
    return "невідома помилка";
}

// Байти об'єкта так, як вони поїдуть у Flash.
template <class T>
[[nodiscard]] std::span<const std::byte> raw_bytes(const T& value) noexcept
{
    static_assert(std::is_trivially_copyable_v<T>, "у Flash їде лише тривіальна розкладка");
    return std::as_bytes(std::span<const T, 1>{&value, 1});
}

// Сирі байти сектора не мають ані типу, ані вирівнювання — копіюємо в об'єкт.
template <class T>
[[nodiscard]] std::optional<T> read_object(std::span<const std::byte> src, std::size_t offset) noexcept
{
    static_assert(std::is_trivially_copyable_v<T>);
    if (src.size() < offset + sizeof(T)) {
        return std::nullopt;
    }
    T out{};
    std::memcpy(&out, src.data() + offset, sizeof(T));
    return out;
}

[[nodiscard]] inline std::uint32_t crc32(std::span<const std::byte> data) noexcept
{
    std::uint32_t crc = 0xFFFFFFFFU;
    for (const std::byte b : data) {
        crc ^= std::to_integer<std::uint32_t>(b);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ (0xEDB88320U & static_cast<std::uint32_t>(-static_cast<std::int32_t>(crc & 1U)));
        }
    }
    return ~crc;
}

}  // namespace cfg
