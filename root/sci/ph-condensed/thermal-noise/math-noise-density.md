# Спектральна щільність теплового шуму (Thermal Noise Power Spectral Density)

Тепловий шум, також відомий як шум Джонсона — Найквіста, являє собою фундаментальний фізичний процес флуктуації електричної напруги та струму в провідниках і резистивних елементах. Цей шум виникає внаслідок хаотичного теплового руху носіїв заряду (електронів у металах і напівпровідниках) при температурі, вищій за абсолютний нуль ($T > 0\text{ K}$).

На відміну від дрібного шуму (shot noise), який зумовлений дискретністю заряду при проходженні потенційного бар'єра, тепловий шум існує в режимі термодинамічної рівноваги за відсутності зовнішнього прикладеного струму чи напруги.

---

## 1. Спектральна щільність напруги та струму

В аналізі сигналів і малошумної схемотехніки тепловий шум описують через **спектральну щільність потужності** (Power Spectral Density, PSD). 

Для резистора з опором $R$ при абсолютній температурі $T$ одностороння спектральна щільність напруги шуму $S_v(f)$ у класичному наближенні є константою в усьому радіочастотному діапазоні (модель «білого шуму»):

$$S_v(f) = 4 k_B T R \quad [\text{В}^2 / \text{Гц}]$$

де:
- $k_B \approx 1.380649 \times 10^{-23}\text{ Дж/К}$ — стала Больцмана;
- $T$ — абсолютна температура елемента в Кельвінах ($T = t\,[^\circ\text{C}] + 273.15$);
- $R$ — активний опір провідника в Омах ($\Omega$).

Зручною практичною величиною є **спектральна щільність напруги шуму** $e_n(f)$, що визначається як квадратний корінь із $S_v(f)$:

$$e_n(f) = \sqrt{S_v(f)} = \sqrt{4 k_B T R} \quad \left[\frac{\text{В}}{\sqrt{\text{Гц}}}\right] \quad \left(\text{або } \frac{\text{нВ}}{\sqrt{\text{Гц}}}\right)$$

За еквівалентною схемою Нортона резистор з тепловим шумом можна подати як ідеальний провідник з адмітансом $G = 1/R$, паралельно якому підключено джерело шуму струму зі спектральною щільністю:

$$S_i(f) = 4 k_B T G = \frac{4 k_B T}{R} \quad [\text{А}^2 / \text{Гц}]$$

$$i_n(f) = \sqrt{S_i(f)} = \sqrt{4 k_B T G} \quad \left[\frac{\text{А}}{\sqrt{\text{Гц}}}\right] \quad \left(\text{або } \frac{\text{пА}}{\sqrt{\text{Гц}}}\right)$$

---

## 2. Обчислення RMS напруги у смузі частот

Середньоквадратичне значення (Root Mean Square, RMS) шуму напруги $V_{\text{rms}}$ у смузі частот від $f_1$ до $f_2$ обчислюється шляхом інтегрування спектральної щільності:

$$V_{\text{rms}}^2 = \int_{f_1}^{f_2} S_v(f) \, df = 4 k_B T R (f_2 - f_1) = 4 k_B T R \Delta f$$

$$V_{\text{rms}} = \sqrt{4 k_B T R \Delta f}$$

де $\Delta f = f_2 - f_1$ — еквівалентна смуга частот (Гц).

### Числовий орієнтир для розробника
За кімнатної температури ($T = 300\text{ К}$, $t \approx 27^\circ\text{C}$):
$$4 k_B T \approx 4 \times (1.38065 \times 10^{-23}) \times 300 = 1.6568 \times 10^{-20}\text{ Дж}$$

Для резистора опором $R = 1\text{ к}\Omega$:
$$e_n = \sqrt{1.6568 \times 10^{-20} \times 1000} \approx 4.07\text{ нВ}/\sqrt{\text{Гц}}$$

Шумова напруга у смузі $\Delta f = 10\text{ кГц}$:
$$V_{\text{rms}} = 4.07\text{ нВ}/\sqrt{\text{Гц}} \times \sqrt{10000} = 407\text{ нВ} = 0.407\text{ мкВ}$$

---

## 3. Еквівалентна шумова смуга (ENBW) та фільтрація

У реальних аналогових трактах смуга обмежується частотною характеристикою фільтрів $H(f)$. Ефективна шумова смуга (Equivalent Noise Bandwidth, ENBW або $B_{\text{n}}$) визначається як ширина прямокутного ідеального фільтра з тим самим підсиленням на середній частоті $A_0$, який пропускає таку саму потужність шуму:

$$B_{\text{n}} = \frac{1}{|A_0|^2} \int_{0}^{\infty} |H(f)|^2 \, df$$

Для однополюсного $RC$-фільтра низьких частот першого порядку з частотою зрізу $f_c = \frac{1}{2\pi R_f C_f}$:

$$B_{\text{n}} = \int_{0}^{\infty} \frac{1}{1 + (f/f_c)^2} \, df = \frac{\pi}{2} f_c \approx 1.571 f_c$$

Таким чином, для $RC$-ланцюга повне інтегральне значення теплового шуму становить:

$$V_{\text{rms, total}}^2 = 4 k_B T R \times \left(\frac{\pi}{2} \cdot \frac{1}{2\pi R C}\right) = \frac{k_B T}{C}$$

$$V_{\text{rms, total}} = \sqrt{\frac{k_B T}{C}}$$

Вираз $V_{\text{rms}} = \sqrt{k_B T / C}$ описує **$kTC$-шум** у вибірково-запам'ятовувальних пристроях (Sample-and-Hold) та АЦП. Зауважимо, що величина цього шуму взагалі не залежить від опору резистора $R$, оскільки збільшення $R$ підвищує спектральну щільність шуму, але пропорційно звужує смугу пропускання.

---

## 4. Квантова поправка Планка

Класична формула Найквіста припускає, що середня енергія на кожну аболютну моду дорівнює $k_B T$ (закони класичної статистичної фізики). На надвисоких частотах (терагерцовий діапазон) або при кріогенних температурах ($h f \ge k_B T$) необхідно застосовувати квантово-механічну формулу Планка з урахуванням нольових коливань вакууму:

$$S_v(f) = 4 R \left( \frac{h f}{e^{\frac{h f}{k_B T}} - 1} + \frac{h f}{2} \right)$$

де $h \approx 6.62607 \times 10^{-34}\text{ Дж}\cdot\text{с}$ — стала Планка.

При $h f \ll k_B T$ вираз $e^{\frac{h f}{k_B T}} - 1 \approx \frac{h f}{k_B T}$, і формула зводиться до класичного виразу $4 k_B T R$. При $T = 300\text{ К}$ границя застосовності класичної формули становить $f \approx 6\text{ ТГц}$, що значно перевищує робочі частоти звичайної мікроелектроніки.

---

## 5. Практична реалізація на C/C++

Нижче наведено бібліотечний модуль C/C++ для обчислення спектральної щільності шуму, розрахунку $V_{\text{rms}}$ з урахуванням ENBW та генерації масиву відліків білого теплового шуму з заданою дисперсією.

```cpp
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Фізичні константи
static const double K_BOLTZMANN = 1.380649e-23; // Дж/К
static const double PLANCK_CONST = 6.62607015e-34; // Дж*с

/**
 * @brief Обчислення спектральної щільності напруги теплового шуму (В^2 / Гц)
 * @param resistance_ohm Опір у Омах
 * @param temp_kelvin Температура в Кельвінах
 * @return Спектральна щільність Sv(f)
 */
double thermal_noise_psd_voltage(double resistance_ohm, double temp_kelvin) {
    if (resistance_ohm < 0.0 || temp_kelvin < 0.0) return 0.0;
    return 4.0 * K_BOLTZMANN * temp_kelvin * resistance_ohm;
}

/**
 * @brief Обчислення спектральної щільності напруги (В / sqrt(Гц))
 */
double thermal_noise_density_v_sqrt_hz(double resistance_ohm, double temp_kelvin) {
    return sqrt(thermal_noise_psd_voltage(resistance_ohm, temp_kelvin));
}

/**
 * @brief Обчислення RMS напруги шуму у заданій смузі (Вольти RMS)
 */
double thermal_noise_rms_voltage(double resistance_ohm, double temp_kelvin, double bandwidth_hz) {
    if (bandwidth_hz < 0.0) return 0.0;
    double psd = thermal_noise_psd_voltage(resistance_ohm, temp_kelvin);
    return sqrt(psd * bandwidth_hz);
}

/**
 * @brief Обчислення kTC шуму для ємності (Вольти RMS)
 */
double ktc_noise_rms_voltage(double capacitance_farad, double temp_kelvin) {
    if (capacitance_farad <= 0.0 || temp_kelvin < 0.0) return 0.0;
    return sqrt((K_BOLTZMANN * temp_kelvin) / capacitance_farad);
}

/**
 * @brief Квантово-механічна спектральна щільність напруги шуму (В^2 / Гц)
 */
double thermal_noise_psd_quantum(double resistance_ohm, double temp_kelvin, double freq_hz) {
    if (temp_kelvin <= 0.0) {
        // При T = 0 K залишаються лише zero-point fluctuations
        return 4.0 * resistance_ohm * (PLANCK_CONST * freq_hz / 2.0);
    }
    double hf = PLANCK_CONST * freq_hz;
    double kt = K_BOLTZMANN * temp_kelvin;
    double thermal_term = hf / (expm1(hf / kt));
    double zero_point_term = hf / 2.0;
    return 4.0 * resistance_ohm * (thermal_term + zero_point_term);
}

/**
 * @brief Генерація гауссівського білого теплового шуму (метод Бокса-Мюллера)
 */
void generate_thermal_noise_samples(float *buffer, size_t count, float rms_voltage) {
    for (size_t i = 0; i < count; i += 2) {
        double u1 = (double)rand() / (double)RAND_MAX;
        double u2 = (double)rand() / (double)RAND_MAX;
        
        // Запобігання log(0)
        while (u1 <= 1e-15) {
            u1 = (double)rand() / (double)RAND_MAX;
        }

        double radius = sqrt(-2.0 * log(u1));
        double theta = 2.0 * M_PI * u2;

        double z0 = radius * cos(theta);
        double z1 = radius * sin(theta);

        buffer[i] = (float)(z0 * rms_voltage);
        if (i + 1 < count) {
            buffer[i + 1] = (float)(z1 * rms_voltage);
        }
    }
}

int main(void) {
    double temp_c = 25.0;
    double temp_k = temp_c + 273.15;
    double r_ohm = 10000.0; // 10 кОм
    double bw_hz = 20000.0; // 20 кГц аудіо смуга

    double psd = thermal_noise_psd_voltage(r_ohm, temp_k);
    double density = thermal_noise_density_v_sqrt_hz(r_ohm, temp_k);
    double v_rms = thermal_noise_rms_voltage(r_ohm, temp_k, bw_hz);
    double v_ktc = ktc_noise_rms_voltage(100e-12, temp_k); // 100 пФ

    printf("=== Аналіз спектральної щільності теплового шуму ===\n");
    printf("Температура: %.2f C (%.2f K)\n", temp_c, temp_k);
    printf("Опір R: %.1f Ом\n", r_ohm);
    printf("Смуга частот: %.1f Гц\n", bw_hz);
    printf("--------------------------------------------------\n");
    printf("Спектральна щільність Sv(f): %.4e V^2/Hz\n", psd);
    printf("Густина шуму e_n:            %.2f nV/sqrt(Hz)\n", density * 1e9);
    printf("RMS шум напруги у смузі:     %.3f uV RMS\n", v_rms * 1e6);
    printf("kTC шум на ємності 100 пФ:   %.3f uV RMS\n", v_ktc * 1e6);

    // Демонстрація генерації 5 відліків шуму
    float noise_samples[5];
    generate_thermal_noise_samples(noise_samples, 5, (float)v_rms);
    printf("\nЗгенеровані часові відліки шуму (uV):\n");
    for (int i = 0; i < 5; i++) {
        printf(" Sample[%d] = %+.3f uV\n", i, noise_samples[i] * 1e6f);
    }

    return 0;
}
```

---

## 6. Висновки

1. **Незалежність від матеріалу**: Спектральна щільність теплового шуму залежить виключно від активного опору $R$ та температури $T$, але не залежить від хімічного складу чи фізичного пристрою провідника.
2. **Білий спектр**: В усіх практичних застосуваннях радіоелектроніки та вимірювальної техніки спектральна щільність теплового шуму є постійною величиною.
3. **Обмеження смуги**: Зменшення RMS напруги шуму досягається застосуванням аналогових та цифрових фільтрів, що зменшують еквівалентну шумову смугу ENBW.
