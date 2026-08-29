// Цифрова частина вимірювального тракту в зборі: АЦП -> проріджування ->
// рухоме середнє на період мережі -> згладжування -> двоточкове калібрування.
//
// Той самий код прошивки проганяється трьома різними апаратними трактами, щоб
// стало видно межу між тим, що можна виправити програмою, і тим, чого не можна:
//
//   1) стробування 1 кГц без антиаліасингового фільтра;
//   2) те саме з RC-ланкою 500 Гц — «фільтр же стоїть»;
//   3) передискретизація 100 кГц з тією ж RC-ланкою і проріджування до 1 кГц.
//
// Складання: c++ -std=c++23 -O2 *.cpp -o afe

#include "afe.hpp"
#include "calibration.hpp"
#include "chain.hpp"
#include "filters.hpp"

#include <algorithm>
#include <cstdint>
#include <format>
#include <iostream>
#include <numeric>
#include <string_view>
#include <vector>

namespace {

constexpr int    kSettleMs            = 300;  // механіка й фільтри після зміни ваги
constexpr int    kCalibrationWindowMs = 400;
constexpr int    kMeasureMs           = 2000;
constexpr double kReferenceWeightKg   = 10.0; // еталонна гиря
constexpr double kTestWeightKg        = 8.0;  // вантаж, який потім «зважуємо»
constexpr std::uint64_t kSeed         = 0xC0FFEEull;

struct Spread {
    std::int32_t mean{0};
    std::int32_t peakToPeak{0};
};

[[nodiscard]] Spread spreadOf(const std::vector<std::int32_t>& samples) noexcept
{
    if (samples.empty()) {
        return {};
    }
    const auto [low, high] = std::ranges::minmax(samples);
    const auto sum = std::accumulate(samples.begin(), samples.end(), std::int64_t{0});
    return {divRound(sum, static_cast<std::int64_t>(samples.size())), high - low};
}

// Ставить вагу, дає тракту заспокоїтись і повертає усереднений код.
// Усереднення тут не косметика: точка калібрування, знята по одному відліку,
// вносить у шкалу весь миттєвий шум тракту назавжди.
[[nodiscard]] std::int32_t averageAtLoad(MeasurementChain& chain,
                                         AnalogFrontEnd& afe,
                                         double kilograms)
{
    afe.setLoad(kilograms);
    for (int ms = 0; ms < kSettleMs; ++ms) {
        (void)chain.advanceOneMillisecond(afe);
    }

    std::vector<std::int32_t> samples;
    samples.reserve(kCalibrationWindowMs);
    for (int ms = 0; ms < kCalibrationWindowMs; ++ms) {
        if (const auto taps = chain.advanceOneMillisecond(afe)) {
            samples.push_back(taps->afterSmoother);
        }
    }
    return spreadOf(samples).mean;
}

struct CaseResult {
    bool             ok{false};
    std::string_view failure{};
    std::int32_t     zeroCode{0};          // код у точці 0 кг, у одиницях тракту
    std::int32_t     spanCode{0};          // код у точці 10 кг
    double           countsPerKilogram{0}; // нормовано до цілих квантів АЦП
    double           meanKilograms{0};
    double           peakToPeakRawGrams{0};
    double           peakToPeakNotchGrams{0};
    double           peakToPeakSmoothGrams{0};
    double           zeroCodeInCounts{0};  // те саме нуль-показання, у квантах АЦП
};

[[nodiscard]] CaseResult runCase(Sampling mode, AntiAliasFilter filter)
{
    AnalogFrontEnd afe{kSeed, filter};
    MeasurementChain chain{mode};

    CaseResult result;
    result.zeroCode = averageAtLoad(chain, afe, 0.0);
    result.spanCode = averageAtLoad(chain, afe, kReferenceWeightKg);

    const auto calibration = TwoPointCalibration::create(result.zeroCode, 0.0,
                                                         result.spanCode, kReferenceWeightKg);
    if (!calibration) {
        result.failure = describe(calibration.error());
        return result;
    }

    afe.setLoad(kTestWeightKg);
    for (int ms = 0; ms < kSettleMs; ++ms) {
        (void)chain.advanceOneMillisecond(afe);
    }

    std::vector<std::int32_t> raw, notched, smoothed;
    raw.reserve(kMeasureMs);
    notched.reserve(kMeasureMs);
    smoothed.reserve(kMeasureMs);

    for (int ms = 0; ms < kMeasureMs; ++ms) {
        if (const auto taps = chain.advanceOneMillisecond(afe)) {
            raw.push_back(taps->raw);
            notched.push_back(taps->afterNotch);
            smoothed.push_back(taps->afterSmoother);
        }
    }

    // Розмах переводимо в грами тим самим калібруванням для всіх трьох точок
    // знімання: фільтри мають одиничний коефіцієнт передачі на постійному струмі.
    const double countsPerGram = calibration->countsPerKilogram() / 1000.0;
    const auto toGrams = [countsPerGram](std::int32_t counts) {
        return static_cast<double>(counts) / countsPerGram;
    };

    result.peakToPeakRawGrams = toGrams(spreadOf(raw).peakToPeak);
    result.peakToPeakNotchGrams = toGrams(spreadOf(notched).peakToPeak);
    result.peakToPeakSmoothGrams = toGrams(spreadOf(smoothed).peakToPeak);
    result.meanKilograms = calibration->toKilograms(spreadOf(smoothed).mean);

    const double scale = chain.rawScale();
    result.countsPerKilogram = calibration->countsPerKilogram() / scale;
    result.zeroCodeInCounts = result.zeroCode / scale;
    result.ok = true;
    return result;
}

void printRow(std::string_view title, const CaseResult& r)
{
    if (!r.ok) {
        std::cout << std::format("| {:<38} | {}\n", title, r.failure);
        return;
    }
    std::cout << std::format("| {:<38} | {:>8} | {:>8} | {:>7.2f} | {:>7.3f} | {:>8.0f} | {:>8.0f} | {:>9.0f} |\n",
                             title, r.zeroCode, r.spanCode, r.countsPerKilogram,
                             r.meanKilograms, r.peakToPeakRawGrams,
                             r.peakToPeakNotchGrams, r.peakToPeakSmoothGrams);
}

} // namespace

int main()
{
    const double nominal = nominalCountsPerKilogram();

    std::cout << "Тракт: міст 2 мВ/В -> AD620 (G = " << std::format("{:.1f}", kInAmpGain)
              << ") -> зміщення 1.65 В -> АЦП 12 біт, Vref = 3.3 В\n";
    std::cout << std::format("Квант АЦП        : {:.3f} мкВ\n",
                             kAdcReference / kAdcLevels * 1e6);
    std::cout << std::format("Розрахунково     : {:.2f} кванта на кілограм ({:.1f} на межі 20 кг)\n",
                             nominal, nominal * 20.0);
    std::cout << "Завади           : 50 Гц залишкова диференційна + ШІМ 980 Гц + тепловий шум\n";
    std::cout << std::format("Прошивка         : рухоме середнє {} відліків (нуль на 50 Гц) + EMA alpha = 1/{}\n\n",
                             kNotchWindow, 1u << kSmootherShift);

    const CaseResult naked = runCase(Sampling::Direct, AntiAliasFilter::Absent);
    const CaseResult filtered = runCase(Sampling::Direct, AntiAliasFilter::Present);
    const CaseResult oversampled = runCase(Sampling::Oversampled, AntiAliasFilter::Present);

    std::cout << std::format("Вантаж {:.1f} кг, вікно спостереження {:.1f} с; розмах — у грамах\n\n",
                             kTestWeightKg, kMeasureMs / 1000.0);
    std::cout << std::format("| {:<38} | {:>8} | {:>8} | {:>7} | {:>7} | {:>8} | {:>8} | {:>9} |\n",
                             "тракт", "код 0 кг", "код 10кг", "кв./кг", "кг", "розмах",
                             "після MA", "після EMA");
    printRow("1 кГц, без антиаліасингового ФНЧ", naked);
    printRow("1 кГц, RC 500 Гц перед АЦП", filtered);
    printRow("100 кГц + RC 500 Гц, проріджування", oversampled);

    if (!naked.ok || !filtered.ok || !oversampled.ok) {
        std::cerr << "Калібрування не пройшло — далі порівнювати нема чого.\n";
        return 1;
    }

    std::cout << "\nЩо тут видно.\n";
    std::cout << "Завада 980 Гц при стробуванні 1 кГц повертається на |980 - 1000| = 20 Гц.\n";
    std::cout << std::format("Рухоме середнє з вікном {} має нуль на 50 Гц, а не на 20 Гц: "
                             "{:.0f} г розмаху лишаються {:.0f} г.\n",
                             kNotchWindow, naked.peakToPeakRawGrams, naked.peakToPeakSmoothGrams);
    std::cout << std::format("RC-ланка 500 Гц послаблює 980 Гц лише вдвічі — {:.0f} г замість {:.0f} г:\n",
                             filtered.peakToPeakSmoothGrams, naked.peakToPeakSmoothGrams);
    std::cout << "один полюс на пів октави від Найквіста нічого не вирішує.\n";
    std::cout << std::format("Передискретизація відсуває Найквіста на 50 кГц, і та сама RC-ланка\n"
                             "разом із проріджувачем лишає {:.0f} г розмаху.\n",
                             oversampled.peakToPeakSmoothGrams);

    // Що показав би той самий тракт без калібрування, за паспортними номіналами.
    const double zeroErrorKg = (oversampled.zeroCodeInCounts - kNominalZeroCode) / nominal;
    const double gainErrorPercent = (oversampled.countsPerKilogram / nominal - 1.0) * 100.0;
    const double uncalibratedKg =
        kTestWeightKg * oversampled.countsPerKilogram / nominal + zeroErrorKg;

    std::cout << "\nЧому двох точок не обійти.\n";
    std::cout << std::format("Порожня платформа дає код {:.1f} замість розрахункових {}:\n",
                             oversampled.zeroCodeInCounts, kNominalZeroCode);
    std::cout << std::format("несиметрія моста і зсув середньої точки — це {:+.3f} кг сталої похибки.\n",
                             zeroErrorKg);
    std::cout << std::format("Нахил шкали розійшовся з паспортним на {:+.2f} % (розкид R_g і Vref).\n",
                             gainErrorPercent);
    std::cout << std::format("Перерахунок за номіналами дав би {:.3f} кг замість {:.3f} кг;\n",
                             uncalibratedKg, kTestWeightKg);
    std::cout << std::format("двоточкове калібрування показує {:.3f} кг, не знаючи жодного номіналу.\n",
                             oversampled.meanKilograms);

    return 0;
}
