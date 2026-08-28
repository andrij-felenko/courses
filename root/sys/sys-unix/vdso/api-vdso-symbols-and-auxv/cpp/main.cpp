#include <cstdint>
#include <array>

// C++20 еквівалент структури vdso_data з вирівнюванням
struct VdsoTimestamp {
    std::uint64_t sec;   // Секунди поточного часу
    std::uint64_t nsec;  // Наносекунди поточного часу
};

struct VdsoData {
    std::uint32_t seq;        // Лічильник послідовності Seqlock
    std::int32_t  clock_mode; // Режим апаратного таймера (VDSO_CLOCKMODE_*)
    std::uint64_t cycle_last; // Значення TSC під час тику ядра
    std::uint64_t mask;       // Маска розрядності лічильника
    std::uint32_t mult;       // Множник конвертації у наносекунди
    std::uint32_t shift;      // Зсув нормування
    
    static constexpr std::size_t kClockBases = 4;
    std::array<VdsoTimestamp, kClockBases> basetime; // Базовий час годинників
    
    std::int32_t  tz_minuteswest;
    std::int32_t  tz_dsttime;
    
    std::uint32_t hrtimer_res;
    std::uint32_t unused;
};
