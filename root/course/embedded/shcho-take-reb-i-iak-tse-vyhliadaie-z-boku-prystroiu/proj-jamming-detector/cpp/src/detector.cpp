#include "ew/detector.hpp"

#include <algorithm>
#include <cstdlib>

namespace ew {
namespace {

// Пороги матриці правил: робоча точка ланки 868 МГц з LoRa-модемом.
constexpr std::int16_t  kRssiSpotMinDbm = -65;    // «сигнал сильний»
constexpr std::int16_t  kRssiBarrageMinDbm = -40; // вхід забитий по стелю
constexpr std::int8_t   kSnrJamMaxDb = 0;
constexpr std::uint8_t  kAgcSaturatedMax = 30;
constexpr std::uint8_t  kPerJamMinPct = 75;
constexpr std::uint8_t  kPerPulseMinPct = 40;
constexpr std::uint32_t kRssiPulseVarMin = 120;   // дБ²
constexpr std::uint8_t  kRssiPulseStepMinDb = 20;
constexpr std::int16_t  kRssiWeakMaxDbm = -105;
constexpr std::int32_t  kEscThrottleDeltaPct = 25;

constexpr std::uint16_t kSpoofCnrX10 = 510;       // 51.0 дБ-Гц
constexpr std::uint32_t kSpoofMadMax = 25;        // 2.5 дБ-Гц
constexpr std::size_t   kSpoofHighPct = 70;
constexpr std::int32_t  kDopplerSpreadMinHz = 300;
constexpr std::size_t   kSpoofMinSats = 4;

} // namespace

std::string_view name(Threat threat) noexcept
{
    using namespace std::string_view_literals;
    switch (threat) {
        case Threat::None:            return "none"sv;
        case Threat::WeakSignal:      return "weak"sv;
        case Threat::SpotJamming:     return "spot"sv;
        case Threat::BarrageBlocking: return "barrage"sv;
        case Threat::PulseJamming:    return "pulse"sv;
        case Threat::GnssSpoofing:    return "spoof"sv;
    }
    return "?"sv;
}

void Detector::push(const RfSample& sample) noexcept
{
    m_window[m_head] = sample;
    m_head = (m_head + 1) % kWindow;
    if (m_count < kWindow) {
        ++m_count;
    }
}

const RfSample& Detector::at(std::size_t k) const noexcept
{
    return m_window[(m_head + kWindow - m_count + k) % kWindow];
}

std::optional<RfStats> Detector::stats() const noexcept
{
    if (m_count < kMinFill) {
        return std::nullopt;
    }

    const auto n = static_cast<std::int32_t>(m_count);
    RfStats st{};
    st.samples = static_cast<std::uint8_t>(m_count);

    std::int32_t  rssi_acc = 0;
    std::int32_t  snr_acc = 0;
    std::uint32_t agc_acc = 0;
    std::uint8_t  crc_errors = 0;

    for (std::size_t k = 0; k < m_count; ++k) {
        const RfSample& s = at(k);
        rssi_acc += s.rssi_dbm;
        snr_acc += s.snr_db;
        agc_acc += s.agc_gain;
        crc_errors = static_cast<std::uint8_t>(crc_errors + (s.crc_error ? 1 : 0));
        st.sync_hits = static_cast<std::uint8_t>(st.sync_hits + (s.preamble ? 1 : 0));
    }

    st.avg_rssi_dbm = static_cast<std::int16_t>(rssi_acc / n);
    st.avg_snr_db = static_cast<std::int8_t>(snr_acc / n);
    st.avg_agc = static_cast<std::uint8_t>(agc_acc / static_cast<std::uint32_t>(n));
    st.per_pct = static_cast<std::uint8_t>(crc_errors * 100 / n);

    std::uint32_t var_acc = 0;
    for (std::size_t k = 0; k < m_count; ++k) {
        const std::int32_t diff = at(k).rssi_dbm - st.avg_rssi_dbm;
        var_acc += static_cast<std::uint32_t>(diff * diff);
    }
    st.rssi_variance = var_acc / static_cast<std::uint32_t>(n);

    // Багатопроменеві провали рухаються повільно — доплерівське розширення
    // обмежує швидкість зміни (20-30 дБ за секунду, тобто ≈3 дБ за крок
    // 100 мс). Імпульсна завада перекидає рівень за один інтервал.
    std::int32_t max_step = 0;
    for (std::size_t k = 1; k < m_count; ++k) {
        const std::int32_t step = std::abs(at(k).rssi_dbm - at(k - 1).rssi_dbm);
        max_step = std::max(max_step, step);
    }
    st.max_step_db = static_cast<std::uint8_t>(std::min<std::int32_t>(max_step, 255));

    return st;
}

bool Detector::escNoiseSuspected() const noexcept
{
    // Власні регулятори обертів шумлять синхронно з газом. Якщо побиті кадри
    // лягають саме на високий газ — це не РЕБ, а власна плата.
    std::int32_t bad_sum = 0;
    std::int32_t good_sum = 0;
    std::int32_t bad = 0;
    std::int32_t good = 0;

    for (std::size_t k = 0; k < m_count; ++k) {
        const RfSample& s = at(k);
        if (s.crc_error) {
            bad_sum += s.throttle_pct;
            ++bad;
        } else {
            good_sum += s.throttle_pct;
            ++good;
        }
    }

    if (bad == 0 || good == 0) {
        return false; // порівнювати нема з чим — нічого не блокуємо
    }
    return (bad_sum / bad) - (good_sum / good) >= kEscThrottleDeltaPct;
}

Threat Detector::classify(const RfStats& st) const noexcept
{
    // Загороджувальна: рівень уперся у стелю, AGC збив підсилення до підлоги,
    // синхрослова не знайдено жодного разу.
    if (st.avg_rssi_dbm >= kRssiBarrageMinDbm && st.avg_agc <= kAgcSaturatedMax &&
        st.sync_hits == 0) {
        return Threat::BarrageBlocking;
    }

    // Прицільна: сигнал сильний, а SNR провалився. Саме ця пара відрізняє
    // глушіння від затінення корпусом, де RSSI і SNR падають разом.
    if (st.avg_rssi_dbm >= kRssiSpotMinDbm && st.avg_snr_db <= kSnrJamMaxDb &&
        st.per_pct >= kPerJamMinPct && st.sync_hits <= 1) {
        return Threat::SpotJamming;
    }

    // Імпульсна: велика дисперсія ПЛЮС миттєвий стрибок між сусідніми
    // вибірками (інакше це багатопроменевість), і не власні ESC.
    if (st.rssi_variance >= kRssiPulseVarMin && st.max_step_db >= kRssiPulseStepMinDb &&
        st.per_pct >= kPerPulseMinPct && !escNoiseSuspected()) {
        return Threat::PulseJamming;
    }

    // Просто далеко або затінило конструкцією: рівень і SNR просіли разом.
    if (st.avg_rssi_dbm <= kRssiWeakMaxDbm && st.per_pct >= kPerJamMinPct) {
        return Threat::WeakSignal;
    }

    return Threat::None;
}

bool Detector::spoofed(const GnssFrame& gnss) noexcept
{
    const auto sats = gnss.sats;
    if (sats.size() < kSpoofMinSats) {
        return false;
    }

    // Найгрубіші ознаки: годинник приймача стрибнув або координата поїхала
    // без жодного руху за даними інерціального вимірювача.
    if (gnss.clock_jump || gnss.position_jump_without_imu) {
        return true;
    }

    const auto n = static_cast<std::uint32_t>(sats.size());
    std::uint32_t cnr_sum = 0;
    std::size_t   high_cnr = 0;
    for (const GnssSat& s : sats) {
        cnr_sum += s.cnr_x10;
        if (s.cnr_x10 >= kSpoofCnrX10) {
            ++high_cnr;
        }
    }
    if (high_cnr * 100 / sats.size() < kSpoofHighPct) {
        return false;
    }

    // Середнє абсолютне відхилення замість СКВ: без кореня і без плаваючої коми.
    const auto avg = static_cast<std::int32_t>(cnr_sum / n);
    std::uint32_t dev_sum = 0;
    for (const GnssSat& s : sats) {
        dev_sum += static_cast<std::uint32_t>(std::abs(static_cast<std::int32_t>(s.cnr_x10) - avg));
    }
    // Однорідна енергетика: справжнє сузір'я розкидане по півсфері, рівні
    // не можуть збігтися так щільно.
    if (dev_sum / n <= kSpoofMadMax) {
        return true;
    }

    // Друга ознака тієї ж природи: усі коди приїхали з однієї нерухомої
    // антени, тож доплер у них практично однаковий, а справжні супутники
    // розходяться на кілька кілогерц.
    const auto [lo, hi] = std::ranges::minmax(sats, {}, &GnssSat::doppler_hz);
    return hi.doppler_hz - lo.doppler_hz <= kDopplerSpreadMinHz;
}

Verdict Detector::evaluate(const std::optional<GnssFrame>& gnss, Millis now) noexcept
{
    Threat verdict = Threat::None;

    // Спуфінг навігації не залежить від радіовікна: кадр GNSS самодостатній,
    // тож судимо його навіть на холодному старті.
    if (gnss && spoofed(*gnss)) {
        verdict = Threat::GnssSpoofing;
    } else if (const auto st = stats()) {
        verdict = classify(*st);
    } // інакше вікно ще заповнюється — мовчимо, а не панікуємо

    if (verdict != m_threat) {
        m_threat = verdict;
        m_since = now;
    }
    return Verdict{m_threat, now - m_since};
}

} // namespace ew
