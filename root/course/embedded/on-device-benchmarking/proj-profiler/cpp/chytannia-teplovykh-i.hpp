// hw_counters.h — читання температури/частоти з sysfs.
// sysfs: стан заліза виглядає як файли — "прочитав файл = дізнався значення".
#pragma once
#include <cstdio>
#include <optional>

// Прочитати одне ціле з файлу sysfs. nullopt — файлу нема / не прочитався.
inline std::optional<long> read_sysfs_long(const char* path) {
    FILE* fp = std::fopen(path, "r");
    if (!fp) return std::nullopt;          // лічильника нема на цій платі
    long v = 0;
    int got = std::fscanf(fp, "%ld", &v);
    std::fclose(fp);
    if (got != 1) return std::nullopt;
    return v;
}

// Температура теплової зони, °C. У sysfs вона в ТИСЯЧНИХ градуса:
// 38800 -> 38.8 °C. zone — номер thermal_zoneX.
inline std::optional<double> read_temp_c(int zone) {
    char path[96];
    std::snprintf(path, sizeof(path),
                  "/sys/devices/virtual/thermal/thermal_zone%d/temp", zone);
    auto raw = read_sysfs_long(path);
    if (!raw) return std::nullopt;
    return *raw / 1000.0;                   // мілі-°C -> °C
}

// Поточна частота ядра cpu, МГц. У sysfs вона в кГц.
inline std::optional<double> read_cpu_mhz(int cpu) {
    char path[112];
    std::snprintf(path, sizeof(path),
        "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_cur_freq", cpu);
    auto raw = read_sysfs_long(path);
    if (!raw) return std::nullopt;
    return *raw / 1000.0;                    // кГц -> МГц
}
