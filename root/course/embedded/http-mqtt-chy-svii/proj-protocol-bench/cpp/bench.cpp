// Заміри трьох способів пакування на одному наборі значень (C++23).
//
// На платі збирається з -DBENCH_USE_DWT: лічильник тактів беруть із блоку
// DWT ядра Cortex-M, і в колонці стоять справжні такти. На робочій станції
// той самий код міряє steady_clock і показує наносекунди.
#include "encode.hpp"
#include "receiver.hpp"

#include <array>
#include <chrono>
#include <cstdint>
#include <format>
#include <iostream>
#include <span>
#include <string_view>

namespace {

constexpr unsigned kIterations = 1000;

#if defined(BENCH_USE_DWT)

volatile std::uint32_t& demcr()      { return *reinterpret_cast<volatile std::uint32_t*>(0xE000EDFCU); }
volatile std::uint32_t& dwtCtrl()    { return *reinterpret_cast<volatile std::uint32_t*>(0xE0001000U); }
volatile std::uint32_t& dwtCyccnt()  { return *reinterpret_cast<volatile std::uint32_t*>(0xE0001004U); }

void benchSetup()
{
    demcr() |= (1U << 24);   // TRCENA — без нього блок DWT не тактується
    dwtCyccnt() = 0;
    dwtCtrl() |= 1U;         // CYCCNTENA
}

std::uint32_t benchNow() { return dwtCyccnt(); }
constexpr std::string_view kUnit = "тактів";

#else

void benchSetup() {}

std::uint64_t benchNow()
{
    return static_cast<std::uint64_t>(
        std::chrono::steady_clock::now().time_since_epoch() / std::chrono::nanoseconds{1});
}
constexpr std::string_view kUnit = "нс";

#endif

// Результат складаємо у volatile: інакше -O2 бачить, що він нікуди не йде,
// викидає весь цикл і міряти стає нічого.
template <class Fn>
void measure(std::string_view label, Fn&& fn)
{
    volatile std::size_t sink = 0;
    const auto t0 = benchNow();
    for (unsigned i = 0; i < kIterations; ++i) {
        sink = fn();
    }
    static_cast<void>(sink);
    const auto elapsed = static_cast<double>(benchNow() - t0);
    std::cout << std::format("  {:<28}{:>8.1f} {}\n", label, elapsed / kIterations, kUnit);
}

void hexDump(std::string_view label, std::span<const std::uint8_t> bytes)
{
    std::cout << std::format("  {} ({} Б):", label, bytes.size());
    for (const auto b : bytes) {
        std::cout << std::format(" {:02X}", b);
    }
    std::cout << '\n';
}

void show(std::string_view label, const std::expected<telem::Receiver::Frame, telem::DecodeError>& res)
{
    if (res) {
        std::cout << std::format("  {:<26}-> OK, seq={}\n", label, res->seq);
    } else {
        std::cout << std::format("  {:<26}-> {}\n", label, telem::describe(res.error()));
    }
}

}  // namespace

int main()
{
    using namespace telem;

    constexpr Sample sample{
        .timestamp_s  = 1'718'000'000,
        .temp_centi_c = 2450,   // 24.50 °C
        .humidity_pct = 6020,   // 60.20 %
        .vbat_mv      = 3280,   // 3.280 В
    };

    constexpr std::string_view host  = "iot.example.com";
    constexpr std::string_view token = "b7f3c1a9e5d24816b0c7f3a9e1d5b2c4a6f80931";
    constexpr std::string_view topic = "sensors/node42";

    std::array<char, 512> http_buf{};
    std::array<std::uint8_t, 128> mqtt_buf{};
    std::array<std::uint8_t, 64> bin_buf{};

    const auto http = buildHttpPost(sample, host, token, http_buf);
    const auto mqtt = buildMqttPublishQos1(sample, topic, 1, mqtt_buf);
    const auto bin  = buildBinaryFrame(sample, 100, bin_buf);

    if (!http || !mqtt || !bin) {
        std::cerr << "не вдалося зібрати кадр\n";
        return 1;
    }

    std::cout << "Розмір кадру з тими самими 10 байтами вимірів\n";
    std::cout << std::format("  HTTP POST + JSON   {:4} Б\n", http->size());
    std::cout << std::format("  MQTT PUBLISH QoS1  {:4} Б\n", mqtt->size());
    std::cout << std::format("  власний кадр       {:4} Б\n", bin->size());
    hexDump("бінарний кадр", *bin);
    std::cout << '\n';

    benchSetup();
    std::cout << std::format("Вартість серіалізації ({} повторів)\n", kIterations);
    measure("HTTP POST + JSON", [&] {
        return buildHttpPost(sample, host, token, http_buf).value_or(std::string_view{}).size();
    });
    measure("MQTT PUBLISH QoS1", [&] {
        return buildMqttPublishQos1(sample, topic, 1, mqtt_buf)
            .value_or(std::span<const std::uint8_t>{}).size();
    });
    measure("власний кадр", [&] {
        return buildBinaryFrame(sample, 100, bin_buf).value_or(std::span<const std::uint8_t>{}).size();
    });
    std::cout << '\n';

    // ---- приймальний бік: перевірки на живих кадрах ----
    Receiver rx;
    std::cout << "Перевірки приймача\n";

    const auto good = buildBinaryFrame(sample, 100, bin_buf).value();
    const auto first = rx.accept(good);
    show("цілий кадр seq=100", first);
    if (first) {
        const auto& s = first->sample;
        std::cout << std::format("    розібрано: ts={} t={}.{:02} h={}.{:02} vbat={} мВ\n",
                                 s.timestamp_s,
                                 s.temp_centi_c / 100, s.temp_centi_c % 100,
                                 s.humidity_pct / 100, s.humidity_pct % 100,
                                 s.vbat_mv);
    }

    show("той самий кадр удруге", rx.accept(good));

    static_cast<void>(buildBinaryFrame(sample, 101, bin_buf));
    bin_buf[6] ^= 0x01;   // один перевернутий біт у полі часу — як завада в ефірі
    show("зіпсований біт", rx.accept(std::span{bin_buf}.first(kFrameSize)));

    static_cast<void>(buildBinaryFrame(sample, 101, bin_buf));
    bin_buf[0] = 0x55;
    show("чужий синхробайт", rx.accept(std::span{bin_buf}.first(kFrameSize)));

    const auto next = buildBinaryFrame(sample, 101, bin_buf).value();
    show("обрізана датаграма", rx.accept(next.first(kFrameSize - 3)));
    show("наступний кадр seq=101", rx.accept(next));

    const auto& st = rx.stats();
    std::cout << std::format(
        "\n  прийнято {}, відкинуто: короткі {}, синхробайт {}, тип {}, CRC {}, повтори {}\n",
        st.accepted, st.too_short, st.bad_magic, st.bad_type, st.bad_crc, st.replay);

    return 0;
}
