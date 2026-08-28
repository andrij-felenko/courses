#include <cstdio>
#include <optional>

// Пороги: за трохи до апаратних меж — щоб діяти РАНІШЕ за тротлінг плати.
constexpr double TEMP_WARN_C = 75.0;   // °C: гаряче, час притишити задачу
constexpr double TEMP_CRIT_C = 82.0;   // °C: критично, скинути важке навантаження
constexpr int    VOLT_MIN_MV = 4750;   // мВ: нижче — шина просіла, недовольтаж близько

// Читання температури кристала (Linux: millidegrees у thermal_zone0).
static std::optional<double> read_soc_temp_c() {
    FILE *f = std::fopen("/sys/class/thermal/thermal_zone0/temp", "r");
    if (!f) return std::nullopt;         // не змогли прочитати — не брешемо, віддаємо «нема даних»
    long milli = 0;
    if (std::fscanf(f, "%ld", &milli) != 1) milli = 0;
    std::fclose(f);
    return milli / 1000.0;               // 61000 → 61.0 °C
}

// Реакція на стан живлення й тепла. Повертає рівень тривоги 0..2.
int power_thermal_guard(double temp_c, int rail_mv) {
    int alarm = 0;

    if (rail_mv > 0 && rail_mv < VOLT_MIN_MV) {
        std::printf("УВАГА: шина %d мВ — просадка, недовольтаж близько\n", rail_mv);
        alarm = 2;                       // просадка живлення — одразу важкий рівень
    }

    if (temp_c >= TEMP_CRIT_C) {
        std::printf("КРИТИЧНО: кристал %.1f°C — скидаю важке навантаження\n", temp_c);
        if (alarm < 2) alarm = 2;
    } else if (temp_c >= TEMP_WARN_C) {
        std::printf("гаряче: кристал %.1f°C — притишую задачу\n", temp_c);
        if (alarm < 1) alarm = 1;
    }
    return alarm;                        // 0 норма · 1 притишити · 2 скинути навантаження
}
