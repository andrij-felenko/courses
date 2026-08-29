#include "nav_frame.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <numbers>
#include <span>

namespace gnss {
namespace {

constexpr double kPi = std::numbers::pi;
constexpr std::size_t kSubframeBits = 300;
constexpr std::size_t kPayloadBits  = 192;      // слова 3..10

// Укладає поля підкадру бітами старшим уперед.
class BitWriter {
public:
    explicit BitWriter(std::span<std::uint8_t> dst) noexcept : dst_{dst} {}

    void bits(std::uint32_t value, int len)
    {
        if (cursor_ + static_cast<std::size_t>(len) > dst_.size()) {
            std::cerr << "підкадр переповнено\n";
            return;
        }
        for (int i = len - 1; i >= 0; --i)
            dst_[cursor_++] = static_cast<std::uint8_t>((value >> i) & 1u);
    }

    void pad(int len) { bits(0, len); }

    // Ціле зі знаком у доповняльному коді, з насиченням на межах поля.
    void scaled(double value, double lsb, int len)
    {
        const double limit = std::exp2(len - 1);
        const double raw = std::clamp(std::round(value / lsb), -limit, limit - 1.0);
        bits(static_cast<std::uint32_t>(static_cast<std::int64_t>(raw)) & mask(len), len);
    }

    void scaled_unsigned(double value, double lsb, int len)
    {
        const double raw = std::clamp(std::round(value / lsb), 0.0, static_cast<double>(mask(len)));
        bits(static_cast<std::uint32_t>(raw) & mask(len), len);
    }

    static constexpr std::uint32_t mask(int len) noexcept
    {
        return len >= 32 ? 0xFFFFFFFFu : ((1u << len) - 1u);
    }

private:
    std::span<std::uint8_t> dst_;
    std::size_t cursor_{};
};

// Розширений код Гемінга: набори інформаційних бітів для кожного біта парності.
constexpr std::array kP25{1,2,3,5,6,10,11,12,13,14,17,18,20,23};
constexpr std::array kP26{2,3,4,6,7,11,12,13,14,15,18,19,21,24};
constexpr std::array kP27{1,3,4,5,7,8,12,13,14,15,16,19,20,22};
constexpr std::array kP28{2,4,5,6,8,9,13,14,15,16,17,20,21,23};
constexpr std::array kP29{1,3,5,6,7,9,10,14,15,16,17,18,21,22,24};
constexpr std::array kP30{3,5,6,8,9,10,11,13,15,19,22,23,24};

struct ParityTail { int d29{}, d30{}; };

template <std::size_t N>
int xor_of(std::span<const std::uint8_t, 24> d, const std::array<int, N>& idx, int seed) noexcept
{
    int p = seed;
    for (int i : idx) p ^= d[static_cast<std::size_t>(i - 1)];
    return p & 1;
}

void encode_word(std::span<std::uint8_t, 30> word,
                 std::span<const std::uint8_t, 24> d, ParityTail& tail) noexcept
{
    const int a = tail.d29, b = tail.d30;

    for (std::size_t i = 0; i < 24; ++i) word[i] = static_cast<std::uint8_t>(d[i] ^ b);
    word[24] = static_cast<std::uint8_t>(xor_of(d, kP25, a));
    word[25] = static_cast<std::uint8_t>(xor_of(d, kP26, b));
    word[26] = static_cast<std::uint8_t>(xor_of(d, kP27, a));
    word[27] = static_cast<std::uint8_t>(xor_of(d, kP28, b));
    word[28] = static_cast<std::uint8_t>(xor_of(d, kP29, b));
    word[29] = static_cast<std::uint8_t>(xor_of(d, kP30, a));

    tail = {word[28], word[29]};
}

// Слова 2 і 10 мусять закінчуватися нулями D29 і D30 — два передостанні
// інформаційні біти для того й лишили вільними.
void encode_solved_word(std::span<std::uint8_t, 30> word,
                        std::span<std::uint8_t, 24> d, ParityTail& tail) noexcept
{
    for (int combo = 0; combo < 4; ++combo) {
        d[22] = static_cast<std::uint8_t>(combo >> 1);
        d[23] = static_cast<std::uint8_t>(combo & 1);

        ParityTail probe = tail;
        encode_word(word, d, probe);
        if (word[28] == 0 && word[29] == 0) { tail = probe; return; }
    }
    std::cerr << "не вдалося розв'язати хвостові біти слова\n";
}

int ura_index(double accuracy_m) noexcept
{
    constexpr std::array edge{2.4,3.4,4.85,6.85,9.65,13.65,24.0,48.0,
                              96.0,192.0,384.0,768.0,1536.0,3072.0,6144.0};
    const auto it = std::ranges::find_if(edge, [&](double e) { return accuracy_m <= e; });
    return static_cast<int>(std::ranges::distance(edge.begin(), it));
}

void build_subframe(std::span<std::uint8_t, kSubframeBits> out, int id, double tow,
                    std::span<const std::uint8_t, kPayloadBits> payload, ParityTail& tail)
{
    std::array<std::uint8_t, 24> d{};

    // Слово 1 — TLM з преамбулою 10001011.
    constexpr std::array<std::uint8_t, 8> preamble{1,0,0,0,1,0,1,1};
    std::ranges::copy(preamble, d.begin());
    encode_word(std::span<std::uint8_t, 30>{out.data(), 30}, d, tail);

    // Слово 2 — HOW: лічильник TOW наступного підкадру в одиницях 6 с.
    d.fill(0);
    BitWriter how{d};
    how.bits((static_cast<std::uint32_t>(tow / 6.0) + 1u) & 0x1FFFFu, 17);
    how.bits(0, 1);                       // alert
    how.bits(0, 1);                       // antispoof
    how.bits(static_cast<std::uint32_t>(id), 3);
    how.pad(2);                           // хвостові біти доберемо перебором
    encode_solved_word(std::span<std::uint8_t, 30>{out.data() + 30, 30}, d, tail);

    for (std::size_t w = 0; w < 8; ++w) {
        std::ranges::copy_n(payload.begin() + static_cast<std::ptrdiff_t>(w * 24), 24, d.begin());
        std::span<std::uint8_t, 30> word{out.data() + (2 + w) * 30, 30};
        if (w == 7) encode_solved_word(word, d, tail);
        else        encode_word(word, d, tail);
    }
}

using Payload = std::array<std::uint8_t, kPayloadBits>;

Payload subframe1(const Ephemeris& e)
{
    Payload p{};
    BitWriter w{p};
    w.bits(static_cast<std::uint32_t>(e.week & 0x3FF), 10);   // тут і переповнюється лічильник
    w.bits(1, 2);                                             // коди на L2
    w.bits(static_cast<std::uint32_t>(ura_index(e.accuracy)), 4);
    w.bits(static_cast<std::uint32_t>(e.health & 0x3F), 6);
    w.bits((static_cast<std::uint32_t>(e.iodc) >> 8) & 0x3u, 2);
    w.bits(0, 1);                                             // прапорець L2 P
    w.pad(23 + 24 + 24 + 16);                                 // резерв слів 4..7
    w.scaled(e.tgd, std::exp2(-31), 8);
    w.bits(static_cast<std::uint32_t>(e.iodc) & 0xFFu, 8);
    w.scaled_unsigned(e.toc, 16.0, 16);
    w.scaled(e.af2, std::exp2(-55), 8);
    w.scaled(e.af1, std::exp2(-43), 16);
    w.scaled(e.af0, std::exp2(-31), 22);
    w.pad(2);
    return p;
}

Payload subframe2(const Ephemeris& e)
{
    Payload p{};
    BitWriter w{p};
    w.bits(static_cast<std::uint32_t>(e.iode) & 0xFFu, 8);
    w.scaled(e.crs, std::exp2(-5), 16);
    w.scaled(e.delta_n / kPi, std::exp2(-43), 16);    // назад у напівоберти
    w.scaled(e.m0 / kPi, std::exp2(-31), 32);
    w.scaled(e.cuc, std::exp2(-29), 16);
    w.scaled_unsigned(e.ecc, std::exp2(-33), 32);
    w.scaled(e.cus, std::exp2(-29), 16);
    w.scaled_unsigned(e.sqrt_a, std::exp2(-19), 32);
    w.scaled_unsigned(e.toe, 16.0, 16);
    w.bits(0, 1);                                     // fit interval 4 год
    w.bits(31, 5);                                    // AODO
    w.pad(2);
    return p;
}

Payload subframe3(const Ephemeris& e)
{
    Payload p{};
    BitWriter w{p};
    w.scaled(e.cic, std::exp2(-29), 16);
    w.scaled(e.omega0 / kPi, std::exp2(-31), 32);
    w.scaled(e.cis, std::exp2(-29), 16);
    w.scaled(e.i0 / kPi, std::exp2(-31), 32);
    w.scaled(e.crc, std::exp2(-5), 16);
    w.scaled(e.omega_arg / kPi, std::exp2(-31), 32);
    w.scaled(e.omega_dot / kPi, std::exp2(-43), 24);
    w.bits(static_cast<std::uint32_t>(e.iode) & 0xFFu, 8);
    w.scaled(e.idot / kPi, std::exp2(-43), 14);
    w.pad(2);
    return p;
}

// Сторінка 18 підкадру 4 — іоносфера й шкала UTC; тут їде секунда координації.
Payload subframe4_page18(const NavContext& ctx, GpsTime t)
{
    constexpr std::array a_lsb{0x1p-30, 0x1p-27, 0x1p-24, 0x1p-24};
    constexpr std::array b_lsb{2048.0, 16384.0, 65536.0, 65536.0};

    Payload p{};
    BitWriter w{p};
    w.bits(1, 2);                        // data ID
    w.bits(56, 6);                       // SV ID сторінки
    for (std::size_t i = 0; i < 4; ++i) w.scaled(ctx.alpha[i], a_lsb[i], 8);
    for (std::size_t i = 0; i < 4; ++i) w.scaled(ctx.beta[i],  b_lsb[i], 8);
    w.scaled(0.0, 0x1p-50, 24);          // A1 розходження шкал UTC/GPS
    w.scaled(0.0, 0x1p-30, 32);          // A0
    w.scaled_unsigned(0.0, 4096.0, 8);   // tot
    w.bits(static_cast<std::uint32_t>(t.broadcast_week() & 0xFF), 8);
    w.scaled(ctx.leap.current, 1.0, 8);
    w.bits(static_cast<std::uint32_t>(ctx.leap.wn_lsf & 0xFF), 8);
    w.bits(static_cast<std::uint32_t>(ctx.leap.dn & 0xFF), 8);
    w.scaled(ctx.leap.future, 1.0, 8);
    w.pad(14 + 2);
    return p;
}

// Сторінка 25 підкадру 5 — стан сузір'я.
Payload subframe5_page25(const NavContext& ctx, GpsTime t)
{
    Payload p{};
    BitWriter w{p};
    w.bits(1, 2);
    w.bits(51, 6);
    w.scaled_unsigned(t.tow(), 4096.0, 8);                    // toa
    w.bits(static_cast<std::uint32_t>(t.broadcast_week() & 0xFF), 8);
    for (std::size_t i = 0; i < 24; ++i)
        w.bits(static_cast<std::uint32_t>(ctx.health[i] & 0x3F), 6);
    w.pad(22 + 2);
    return p;
}

}  // namespace

NavFrame::NavFrame(const Ephemeris& eph, const NavContext& ctx, GpsTime frame_start)
    : start_{frame_start.aligned_to(kDuration)}
{
    const std::array<Payload, 5> payloads{
        subframe1(eph), subframe2(eph), subframe3(eph),
        subframe4_page18(ctx, start_), subframe5_page25(ctx, start_)
    };

    std::array<std::uint8_t, kBits> raw{};
    ParityTail tail{};
    for (std::size_t sf = 0; sf < payloads.size(); ++sf) {
        build_subframe(std::span<std::uint8_t, kSubframeBits>{raw.data() + sf * kSubframeBits,
                                                             kSubframeBits},
                       static_cast<int>(sf) + 1,
                       start_.tow() + static_cast<double>(sf) * 6.0,
                       std::span<const std::uint8_t, kPayloadBits>{payloads[sf]},
                       tail);
    }

    std::ranges::transform(raw, bits_.begin(),
                           [](std::uint8_t b) { return static_cast<std::int8_t>(1 - 2 * b); });
}

std::optional<double> NavFrame::bit_position(GpsTime t_tx) const noexcept
{
    const double dt = t_tx - start_;
    if (dt < 0.0 || dt >= kDuration) return std::nullopt;      // кадр треба перебудувати
    return dt * kNavBitRateHz;
}

std::int8_t NavFrame::sign_at(double position) const noexcept
{
    auto index = static_cast<std::int64_t>(position) % static_cast<std::int64_t>(kBits);
    if (index < 0) index += static_cast<std::int64_t>(kBits);
    return bits_[static_cast<std::size_t>(index)];
}

}  // namespace gnss
