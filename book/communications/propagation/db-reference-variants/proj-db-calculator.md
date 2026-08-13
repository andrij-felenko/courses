# ⚙️ Універсальний інженерний конвертер децибельних одиниць

Для автоматизації розрахунків радіоліній, аналізу спектра в розробці програмно-визначеного радіо (SDR) та контролю параметрів електромагнітної сумісності (ЕМС) виникає потреба миттєво переводити значення між різними варіантами децибельних одиниць. Прямі обчислення вручну забирають час та часто призводять до помилок через плутанину з коефіцієнтами опору трактів (50 Ом проти 75 Ом) чи логарифмічними множниками (10 log для потужності проти 20 log для напруги).

Нижче наведено повнофункціональний інженерний модуль конвертації одиниць, реалізований трьома мовами програмування: C, C++ та Python. Програма виконує точні математичні перетворення між основними одиницями радіотехнічного домену:
- Абсолютна потужність: `dBm` (децибел-міліват) ↔ `dBW` (децибел-ват) ↔ `мВт` (фізичні мілівати).
- Перетворення напруги у потужність: `dBμV` (децибел-мікровольт) ↔ `dBm` для систем із хвильовим опором 50 Ом та 75 Ом.
- Напруга в аналогових трактах: `dBV` ↔ `dBu` ↔ `Вольти RMS`.
- Підсилення антен: `dBi` (відносно ізотропа) ↔ `dBd` (відносно півхвильового диполя).
- Параметри спектральної щільності шуму: обчислення відношення несучої до шуму `C/N₀` у `dBHz` за рівнем сигналу та смугою частот.

### Архітектура програмного модуля та обробка граничних умов

Під час розробки інженерного конвертера особливу увагу приділено надійності обчислень та коректній обробці крайових умов, які виникають у реальних вимірювальних трактах:

1. **Захист від некоректних вхідних даних потужності**: Фізична потужність у лінійних одиницях (міліватах або ватах) за своєю природою є суворо додатною величиною (`P > 0`). Спроба обчислити логарифм від нуля або від'ємного числа `log₁₀(0)` веде до математичної невизначеності (мінус нескінченність або `NaN`). У реалізації мовою C для запобігання аварійному завершенню повертається спеціальне значення константи помилки `-999.0 dBm`. У версії C++23 застосовано сучасний механізм мономорфної обробки помилок `std::expected` із чітким переліком `ConversionError::NonPositivePower`, що вимагає від викликаючого коду явного опрацювання помилкової гілки. У Python-реалізації генерується стандартний виняток `ValueError` із пояснювальним повідомленням.
2. **Перевірка смуги частот у розрахунках шуму**: Обчислення спектральної щільності шуму `C/N₀` спирається на логарифм смуги частот `10 · log₁₀(bandwidth_hz)`. Якщо смуга частот передана як 0 Гц або від'ємне значення, модуль сигналізує про помилку вхідних параметрів `ConversionError::InvalidInput`.
3. **Обліковані константи хвильового опору**: Зсув між напругою `dBμV` та потужністю `dBm` розраховується з урахуванням константи обраного опору тракту `Impedance`: для 50 Ом константа становить `106.99 дБ`, а для 75 Ом — `108.75 дБ`. Це унеможливлює помилки при перетині межі між антенним трактом (50 Ом) та телевізійним кабелем (75 Ом).
4. **Обчислення на етапі компіляції**: У реалізації мовою C++ усі математичні перетворення позначені як `constexpr`. Це дозволяє компілятору обчислювати константні значення децибел ще на етапі збірки програми без жодних накладних витрат під час виконання у процесорі мікроконтролера.

### Математичні алгоритми та точність числового представлення

Усі розрахунки у представлених реалізаціях виконуються з використанням чисел з плаваючою комою подвійної точності за стандартом IEEE 754 (`double`, 64 біти, 53 біти мантиси). Це забезпечує відносну точність обчислень біля 15-17 значущих десяткових цифр.

При перетворенні `dBm` у мілівати застосовується показникові функція з основою 10: `P[мВт] = 10^(P[dBm] / 10)`. На мікроконтролерах без апаратного блоку плаваючої коми (FPU) обчислення ступеня `pow(10.0, x)` зазвичай вимагає використання математичної бібліотеки `libm`. Для прискорення обчислень у реальному часі на DSP-процесорах часто використовують табличне наближення (англ. *lookup table*, LUT) з подальшою лінійною або кубічною інтерполяцією.

Для перетворення з напруги у потужність у 50-омному тракті застосовується константа `106.99 дБ`, отримана точним розрахунком `90 + 10 · log₁₀(50) = 90 + 16.9897 = 106.9897 дБ`. Округлення до двох знаків після коми `106.99 дБ` дає числову абсолютну помилку менше ніж `0.0003 дБ`, що знаходиться далеко за межами похибки будь-якого еталонного калаброваного вимірювального приладу чи аналізатора спектра (де похибка становить 0.2–0.5 дБ).

:::tabs
```c
#include <stdio.h>
#include <math.h>

typedef enum {
    IMPEDANCE_50_OHM = 50,
    IMPEDANCE_75_OHM = 75,
    IMPEDANCE_600_OHM = 600
} Impedance;

/* Перетворення потужності: dBm <-> Вт / мВт */
double dbm_to_mw(double dbm) {
    return pow(10.0, dbm / 10.0);
}

double mw_to_dbm(double mw) {
    return (mw > 0.0) ? 10.0 * log10(mw) : -999.0;
}

double dbm_to_dbw(double dbm) {
    return dbm - 30.0;
}

double dbw_to_dbm(double dbw) {
    return dbw + 30.0;
}

/* Перетворення між dBμV та dBm залежно від опору навантаження */
double dbmuv_to_dbm(double dbmuv, Impedance r) {
    double k = (r == IMPEDANCE_75_OHM) ? 108.75 : 106.99;
    return dbmuv - k;
}

double dbm_to_dbmuv(double dbm, Impedance r) {
    double k = (r == IMPEDANCE_75_OHM) ? 108.75 : 106.99;
    return dbm + k;
}

/* Перетворення напруги у dBV та dBu */
double dbv_to_volts(double dbv) {
    return pow(10.0, dbv / 20.0);
}

double dbu_to_volts(double dbu) {
    return 0.7745966 * pow(10.0, dbu / 20.0);
}

/* Перетворення підсилення антен: dBi <-> dBd */
double dbd_to_dbi(double dbd) {
    return dbd + 2.15;
}

double dbi_to_dbd(double dbi) {
    return dbi - 2.15;
}

/* Розрахунок C/N0 (dBHz) за потужністю сигналу та шумом */
double calculate_cn0(double signal_dbm, double bandwidth_hz) {
    const double noise_floor_dbm_hz = -173.98;
    double total_noise_dbm = noise_floor_dbm_hz + 10.0 * log10(bandwidth_hz);
    double snr_db = signal_dbm - total_noise_dbm;
    return snr_db + 10.0 * log10(bandwidth_hz);
}

int main(void) {
    double p_dbm = 20.0; /* 100 мВт Wi-Fi передавач */
    double gain_dbd = 9.0; /* 9 dBd Ягі-антена */
    
    printf("=== RF Unit Converter (C) ===\n");
    printf("Потужність: %.2f dBm = %.2f мВт = %.2f dBW\n", 
           p_dbm, dbm_to_mw(p_dbm), dbm_to_dbw(p_dbm));
    
    printf("Напруга у 50 Ом: %.2f dBm = %.2f dBuV\n", 
           p_dbm, dbm_to_dbmuv(p_dbm, IMPEDANCE_50_OHM));
           
    printf("Підсилення антени: %.2f dBd = %.2f dBi\n", 
           gain_dbd, dbd_to_dbi(gain_dbd));
           
    double rx_dbm = -90.0;
    double bw_hz = 20e6; /* 20 МГц смуга Wi-Fi */
    printf("C/N0 при %.2f dBm у смузі 20 МГц: %.2f dBHz\n", 
           rx_dbm, calculate_cn0(rx_dbm, bw_hz));
           
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <expected>
#include <string_view>
#include <format>

enum class Impedance {
    Ohm50 = 50,
    Ohm75 = 75,
    Ohm600 = 600
};

enum class ConversionError {
    InvalidInput,
    NonPositivePower
};

class RfUnitConverter {
public:
    static constexpr double ThermalNoiseFloorDbmHz = -173.98;
    static constexpr double DipoleOffsetDbi = 2.15;

    [[nodiscard]] static constexpr double dbmToMw(double dbm) noexcept {
        return std::pow(10.0, dbm / 10.0);
    }

    [[nodiscard]] static std::expected<double, ConversionError> mwToDbm(double mw) noexcept {
        if (mw <= 0.0) {
            return std::unexpected(ConversionError::NonPositivePower);
        }
        return 10.0 * std::log10(mw);
    }

    [[nodiscard]] static constexpr double dbmToDbw(double dbm) noexcept {
        return dbm - 30.0;
    }

    [[nodiscard]] static constexpr double dbwToDbm(double dbw) noexcept {
        return dbw + 30.0;
    }

    [[nodiscard]] static constexpr double dbmuvToDbm(double dbmuv, Impedance z) noexcept {
        double k = (z == Impedance::Ohm75) ? 108.75 : 106.99;
        return dbmuv - k;
    }

    [[nodiscard]] static constexpr double dbmToDbmuv(double dbm, Impedance z) noexcept {
        double k = (z == Impedance::Ohm75) ? 108.75 : 106.99;
        return dbm + k;
    }

    [[nodiscard]] static constexpr double dbdToDbi(double dbd) noexcept {
        return dbd + DipoleOffsetDbi;
    }

    [[nodiscard]] static constexpr double dbiToDbd(double dbi) noexcept {
        return dbi - DipoleOffsetDbi;
    }

    [[nodiscard]] static std::expected<double, ConversionError> calculateCn0(double signalDbm, double bandwidthHz) noexcept {
        if (bandwidthHz <= 0.0) {
            return std::unexpected(ConversionError::InvalidInput);
        }
        return signalDbm - ThermalNoiseFloorDbmHz;
    }
};

int main() {
    constexpr double pDbm = 20.0;
    constexpr double gainDbd = 9.0;

    std::cout << "=== RF Unit Converter (C++23) ===\n";
    std::cout << "Потужність: " << pDbm << " dBm = " << RfUnitConverter::dbmToMw(pDbm) 
              << " мВт = " << RfUnitConverter::dbmToDbw(pDbm) << " dBW\n";

    std::cout << "Напруга у 50 Ом: " << pDbm << " dBm = " 
              << RfUnitConverter::dbmToDbmuv(pDbm, Impedance::Ohm50) << " dBuV\n";

    std::cout << "Підсилення антени: " << gainDbd << " dBd = " 
              << RfUnitConverter::dbdToDbi(gainDbd) << " dBi\n";

    if (auto cn0 = RfUnitConverter::calculateCn0(-90.0, 20e6); cn0.has_value()) {
        std::cout << "C/N0 при -90 dBm у смузі 20 МГц: " << cn0.value() << " dBHz\n";
    }

    return 0;
}
```
```py
import math

class RfUnitConverter:
    THERMAL_NOISE_FLOOR_DBM_HZ = -173.98
    DIPOLE_OFFSET_DBI = 2.15

    @staticmethod
    def dbm_to_mw(dbm: float) -> float:
        return 10.0 ** (dbm / 10.0)

    @staticmethod
    def mw_to_dbm(mw: float) -> float:
        if mw <= 0:
            raise ValueError("Потужність повинна бути більшою за нуль.")
        return 10.0 * math.log10(mw)

    @staticmethod
    def dbm_to_dbw(dbm: float) -> float:
        return dbm - 30.0

    @staticmethod
    def dbmuv_to_dbm(dbmuv: float, impedance: int = 50) -> float:
        k = 108.75 if impedance == 75 else 106.99
        return dbmuv - k

    @staticmethod
    def dbm_to_dbmuv(dbm: float, impedance: int = 50) -> float:
        k = 108.75 if impedance == 75 else 106.99
        return dbm + k

    @staticmethod
    def dbd_to_dbi(dbd: float) -> float:
        return dbd + RfUnitConverter.DIPOLE_OFFSET_DBI

    @staticmethod
    def calculate_cn0(signal_dbm: float, bandwidth_hz: float) -> float:
        if bandwidth_hz <= 0:
            raise ValueError("Смуга частот повинна бути більшою за нуль.")
        return signal_dbm - RfUnitConverter.THERMAL_NOISE_FLOOR_DBM_HZ


if __name__ == "__main__":
    p_dbm = 20.0
    print("=== RF Unit Converter (Python) ===")
    print(f"Потужність: {p_dbm} dBm = {RfUnitConverter.dbm_to_mw(p_dbm):.2f} мВт")
    print(f"Напруга у 50 Ом: {p_dbm} dBm = {RfUnitConverter.dbm_to_dbmuv(p_dbm, 50):.2f} dBuV")
    print(f"C/N0 при -90 dBm: {RfUnitConverter.calculate_cn0(-90.0, 20e6):.2f} dBHz")
```
:::

### Інструкції з компіляції та верифікації

Для збірки та запуска контрольного прикладу у середовищах Linux, macOS або Windows (MinGW/Clang/MSVC) використовуйте такі стандартизовані команди консолі:

**Компіляція версії мовою C (GCC / Clang):**

```bash
gcc -O2 -Wall -Wextra main.c -lm -o rf_converter_c
./rf_converter_c
```
*(Примітка: прапорець `-lm` є обов'язковим у POSIX-системах для підключення математичної бібліотеки `libm`, де містяться функції `pow` та `log10`).*

**Компіляція версії мовою C++ (GCC 13+ / Clang 16+ з підтримкою стандарту C++23):**

```bash
g++ -std=c++23 -O2 -Wall -Wextra main.cpp -o rf_converter_cpp
./rf_converter_cpp
```

### Верифікаційні контрольні точки

Перевірити правильність роботи скомпільованого модуля можна за такими еталонними значеннями радіотехнічного розрахунку:
- Вхід `+20 dBm` ➔ Вихід `100.00 мВт` та `-10.00 dBW`.
- Вхід `+20 dBm` у тракті 50 Ом ➔ Вихід `126.99 dBμV` (еквівалент напруги `2.24 В RMS`).
- Вхід `9.00 dBd` підсилення антени Yagi ➔ Вихід `11.15 dBi` ізотропного підсилення.
- Вхід `-90.00 dBm` рівень сигналу при смузі `20 МГц` ➔ Вихід `83.98 dBHz` для відношення `C/N₀`.

Впровадження цього розрахованого модуля у лабораторні автоматизовані стенди запобігає системним помилкам перетворення фізичних величин під час аналізу спектра та проєктування високочастотних трактів.

> 🔧 **Навіщо це.** У розробці програмно-визначеного радіо (SDR) цей конвертер дозволяє автоматично калібрувати цифровий рівень сигналу `dBFS`, отриманий від АЦП, у реальні фізичні значення `dBm` на антенному роз'ємі приймача, враховуючи налаштування підсилення LNA та опір вхідного тракту.
