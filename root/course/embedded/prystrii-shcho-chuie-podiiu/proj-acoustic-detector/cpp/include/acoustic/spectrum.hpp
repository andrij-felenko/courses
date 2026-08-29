// Кадровий фронтенд: 256 відліків → 32 логарифмічні мел-ознаки int8_t.
//
// Таблиці тут ніхто не набирає руками й не вставляє з генератора: вікно
// Хеммінга, чверть періоду синуса для FFT і межі мел-смуг рахує компілятор
// у constexpr-обчисленні. У прошивку вони потрапляють такими самими
// константами в .rodata, але помилитися в цифрі вже неможливо, а змінити
// частоту зрізу мел-банку — це правка одного числа, а не перегенерація файла.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace acoustic {

inline constexpr std::size_t kSampleRate   = 16000;
inline constexpr std::size_t kFrameSamples = 256;   // 16.0 мс
inline constexpr std::size_t kFftSize      = 512;   // кадр + доповнення нулями
inline constexpr std::size_t kMelBins      = 32;

namespace detail {

inline constexpr double kPi = 3.14159265358979323846;

// Ряд Тейлора після зведення аргументу до [-π/2, π/2]: на цьому проміжку
// дев'яти доданків вистачає з запасом у кілька порядків над Q15.
constexpr double sine(double x) noexcept
{
    while (x >  kPi) { x -= 2.0 * kPi; }
    while (x < -kPi) { x += 2.0 * kPi; }
    if (x >  kPi / 2.0) { x =  kPi - x; }
    if (x < -kPi / 2.0) { x = -kPi - x; }

    double term = x;
    double sum  = x;
    for (int n = 1; n <= 9; ++n) {
        term *= -x * x / static_cast<double>((2 * n) * (2 * n + 1));
        sum  += term;
    }
    return sum;
}

constexpr double cosine(double x) noexcept { return sine(x + kPi / 2.0); }

// ln через ряд для area tangens: після зведення мантиси до [0.75, 1.5]
// аргумент ряду не перевищує 0.2, і збіжність миттєва.
constexpr double naturalLog(double x) noexcept
{
    int exponent = 0;
    while (x > 1.5)  { x /= 2.0; ++exponent; }
    while (x < 0.75) { x *= 2.0; --exponent; }

    const double t  = (x - 1.0) / (x + 1.0);
    const double t2 = t * t;

    double term = t;
    double sum  = t;
    for (int n = 1; n < 12; ++n) {
        term *= t2;
        sum  += term / static_cast<double>(2 * n + 1);
    }
    return 2.0 * sum + static_cast<double>(exponent) * 0.6931471805599453;
}

constexpr double naturalExp(double x) noexcept
{
    constexpr double kLn2 = 0.6931471805599453;

    int k = static_cast<int>(x / kLn2 + (x < 0.0 ? -0.5 : 0.5));
    const double r = x - static_cast<double>(k) * kLn2;

    double term = 1.0;
    double sum  = 1.0;
    for (int n = 1; n < 14; ++n) {
        term *= r / static_cast<double>(n);
        sum  += term;
    }

    while (k > 0) { sum *= 2.0; --k; }
    while (k < 0) { sum /= 2.0; ++k; }
    return sum;
}

constexpr std::int16_t toQ15(double v) noexcept
{
    const double scaled = v * 32768.0;
    const long rounded = static_cast<long>(scaled >= 0.0 ? scaled + 0.5 : scaled - 0.5);

    if (rounded > 32767) { return 32767; }
    if (rounded < -32768) { return -32768; }
    return static_cast<std::int16_t>(rounded);
}

}  // namespace detail

// Вікно Хеммінга у Q15.
inline constexpr auto kHammingQ15 = [] {
    std::array<std::int16_t, kFrameSamples> window{};
    for (std::size_t n = 0; n < window.size(); ++n) {
        const double phase = 2.0 * detail::kPi * static_cast<double>(n) /
                             static_cast<double>(kFrameSamples - 1);
        window[n] = detail::toQ15(0.54 - 0.46 * detail::cosine(phase));
    }
    return window;
}();

// Чверть періоду синуса: sin(2π·k/512), k = 0…128. Решту трьох чвертей
// дає симетрія, тому в пам'яті лежить лише 258 байтів.
inline constexpr auto kSinQ15Quarter = [] {
    std::array<std::int16_t, kFftSize / 4 + 1> table{};
    for (std::size_t k = 0; k < table.size(); ++k) {
        const double phase = 2.0 * detail::kPi * static_cast<double>(k) /
                             static_cast<double>(kFftSize);
        table[k] = detail::toQ15(detail::sine(phase));
    }
    return table;
}();

// Межі трикутників мел-банку в комірках FFT: рівномірна сітка в мел-шкалі
// від 64 Гц до 7600 Гц. Смуга m живе на [edge[m], edge[m+2]] з вершиною
// в edge[m+1], тож сусідні смуги перекриваються наполовину.
inline constexpr auto kMelEdges = [] {
    constexpr double kLowHz  = 64.0;
    constexpr double kHighHz = 7600.0;

    constexpr auto toMel = [](double hz) {
        return 1127.0 * detail::naturalLog(1.0 + hz / 700.0);
    };
    constexpr auto toHz = [](double mel) {
        return 700.0 * (detail::naturalExp(mel / 1127.0) - 1.0);
    };

    std::array<std::uint16_t, kMelBins + 2> edges{};
    const double melLow  = toMel(kLowHz);
    const double melHigh = toMel(kHighHz);

    for (std::size_t i = 0; i < edges.size(); ++i) {
        const double mel = melLow + (melHigh - melLow) * static_cast<double>(i) /
                                        static_cast<double>(kMelBins + 1);
        auto bin = static_cast<std::uint16_t>(toHz(mel) * static_cast<double>(kFftSize) /
                                              static_cast<double>(kSampleRate));
        // На низьких частотах сусідні смуги інакше злипаються в одну комірку,
        // а трикутник нульової ширини поділив би на нуль.
        if (i > 0 && bin <= edges[i - 1]) {
            bin = static_cast<std::uint16_t>(edges[i - 1] + 1);
        }
        edges[i] = bin;
    }
    return edges;
}();

// Комплексна FFT на місці. Кожен щабель ділить результат на 2 — інакше сума
// 512 доданків вилітає за int16 на першому ж гучному кадрі, а насичення
// знищило б спектр. На виході стоїть X[k] / N.
void fft(std::span<std::int16_t, kFftSize> re, std::span<std::int16_t, kFftSize> im) noexcept;

// Класичний MFCC після логарифма робить ще й дискретне косинусне
// перетворення, щоб розкорелювати смуги. Згортковій мережі це шкодить: DCT
// перемішує сусідні частоти, а згортка 3×3 саме на сусідстві смуг і тримається.
// Тому конвеєр спиняється на логарифмічних мел-енергіях.
class MelFrontend {
public:
    void reset() noexcept { previous_ = 0; }

    // Один кадр: преакцент → вікно → FFT → мел-банк → log2 → int8.
    void process(std::span<const std::int16_t, kFrameSamples> frame,
                 std::span<std::int8_t, kMelBins> out) noexcept;

private:
    std::int16_t previous_{0};

    // Робочі масиви живуть у самому фронтенді, а не в статиці файла: два
    // мікрофонні канали — два незалежні примірники, і жодного спільного
    // стану між ними. Платня — 2 КБ на примірник.
    std::array<std::int16_t, kFftSize> re_{};
    std::array<std::int16_t, kFftSize> im_{};
};

}  // namespace acoustic
