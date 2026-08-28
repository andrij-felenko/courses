#include <cstdint>
#include <cstddef>
#include <array>
#include <string_view>

// Сорти за спаданням: назва + мінімальна гарантована частота, МГц.
struct SpeedBin { std::string_view name; std::uint32_t min_mhz; };

static constexpr std::array<SpeedBin, 4> BINS = {{
    { "топ-сорт",   3600 },   // найдорожчий
    { "середній",   3200 },
    { "базовий",    2800 },
    { "молодший",   2400 },
}};

// Запас: відсоток на старіння/нагрів + абсолютна добавка на просідання живлення.
constexpr std::uint32_t GUARD_PERCENT = 7;    // 7% на деградацію за роки + температуру
constexpr std::uint32_t GUARD_FIXED   = 50;   // ще 50 МГц «жорсткого» запасу на просідання Vdd

// Гарантована частота = виміряна fmax мінус guard-band.
static std::uint32_t guaranteed_mhz(std::uint32_t fmax_mhz) {
    std::uint32_t margin = (fmax_mhz * GUARD_PERCENT) / 100 + GUARD_FIXED;
    return (fmax_mhz > margin) ? (fmax_mhz - margin) : 0;
}

// Повертає індекс найвищого сорту, чию планку кристал ще тримає (−1 = брак).
static int classify(std::uint32_t fmax_mhz) {
    std::uint32_t guaranteed = guaranteed_mhz(fmax_mhz);
    for (std::size_t i = 0; i < BINS.size(); ++i)   // від найдорожчого вниз
        if (guaranteed >= BINS[i].min_mhz)
            return static_cast<int>(i);
    return -1;                                       // навіть молодший сорт не тягне
}
