/* 
 * spectrum_calc.c — Повна промислова реалізація калькулятора ЕМ-спектра мовою C (C99/C11)
 * Модуль призначений для вбудованих систем, вимірювальних приладів та систем моніторингу.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Фундаментальні фізичні константи */
#define C_SPEED     299792458.0         /* Швидкість світла в м/с (точна) */
#define H_PLANCK    6.62607015e-34      /* Константа Планка в Дж·с */
#define EV_JOULE    1.602176634e-19     /* 1 еВ у джоулях */
#define WIEN_CONST  2.89777195e-3       /* Константа зсуву Віна в м·К */
#define CU_SIGMA    5.8e7               /* Провідність міді у См/м */
#define MU_0        (4.0 * M_PI * 1e-7) /* Магнітна стала вакууму Гн/м */

/* Перелічуваний тип діапазонів спектра */
typedef enum {
    BAND_RADIO,
    BAND_MICROWAVE,
    BAND_INFRARED,
    BAND_VISIBLE,
    BAND_ULTRAVIOLET,
    BAND_XRAY,
    BAND_GAMMA
} em_band_t;

/* Структура паспортних даних ЕМ-сигналу */
typedef struct {
    double frequency_hz;      /* Частота в Гц */
    double wavelength_m;      /* Довжина хвилі у вакуумі в м */
    double energy_joules;     /* Енергія фотона у джоулях */
    double energy_ev;         /* Енергія фотона в електронвольтах */
    double skin_depth_cu_m;   /* Глибина скін-шару в міді в м */
    double wien_temp_k;       /* Еквівалентна температура чорного тіла в К */
    em_band_t band;           /* Спектральний діапазон */
    bool is_ionizing;         /* Прапор іонізуючої здатності */
    const char* band_name;    /* Назва діапазону українською */
} spectrum_info_t;

/* Повертає текстову назву діапазону */
const char* get_band_name(em_band_t band) {
    switch (band) {
        case BAND_RADIO:       return "Радіохвилі (Radio)";
        case BAND_MICROWAVE:   return "Мікрохвилі (Microwave / НВЧ)";
        case BAND_INFRARED:    return "Інфрачервоне випромінювання (IR)";
        case BAND_VISIBLE:     return "Видиме світло (Visible)";
        case BAND_ULTRAVIOLET: return "Ультрафіолет (UV)";
        case BAND_XRAY:        return "Рентгенівське випромінювання (X-Ray)";
        case BAND_GAMMA:       return "Гамма-випромінювання (Gamma)";
        default:               return "Невідомий діапазон";
    }
}

/* Обчислює паспортні дані сигналу за частотою */
spectrum_info_t calculate_by_frequency(double freq_hz) {
    spectrum_info_t info;
    if (freq_hz <= 0.0) {
        freq_hz = 1e-12; /* Захист від нульової чи від'ємної частоти */
    }

    info.frequency_hz = freq_hz;
    info.wavelength_m = C_SPEED / freq_hz;
    info.energy_joules = H_PLANCK * freq_hz;
    info.energy_ev = info.energy_joules / EV_JOULE;
    
    /* Обчислення скін-шару у мідному провіднику */
    double omega = 2.0 * M_PI * freq_hz;
    info.skin_depth_cu_m = sqrt(2.0 / (omega * MU_0 * CU_SIGMA));
    
    /* Розрахунок температури за законом зсуву Віна */
    info.wien_temp_k = WIEN_CONST / info.wavelength_m;

    /* Класифікація за частотою */
    if (freq_hz < 3.0e9) {
        info.band = BAND_RADIO;
    } else if (freq_hz < 3.0e11) {
        info.band = BAND_MICROWAVE;
    } else if (freq_hz < 4.0e14) {
        info.band = BAND_INFRARED;
    } else if (freq_hz < 7.9e14) {
        info.band = BAND_VISIBLE;
    } else if (freq_hz < 3.0e16) {
        info.band = BAND_ULTRAVIOLET;
    } else if (freq_hz < 3.0e19) {
        info.band = BAND_XRAY;
    } else {
        info.band = BAND_GAMMA;
    }

    /* Поріг іонізації прийнято на рівні 10 еВ (середній УФ) */
    info.is_ionizing = (info.energy_ev >= 10.0);
    info.band_name = get_band_name(info.band);

    return info;
}

/* Форматований вивід результатів у консоль */
void print_spectrum_card(const spectrum_info_t* info) {
    printf("\n==================================================\n");
    printf("   ПАСПОРТНА КАРТКА ЕЛЕКТРОМАГНІТНОГО СИГНАЛУ    \n");
    printf("==================================================\n");
    printf(" Частота (f):          %.4e Гц\n", info->frequency_hz);
    printf(" Довжина хвилі (λ):   %.4e м\n", info->wavelength_m);
    printf(" Енергія фотона (E):   %.4e еВ (%.4e Дж)\n", info->energy_ev, info->energy_joules);
    printf(" Скін-шар у міді (δ):  %.4e м\n", info->skin_depth_cu_m);
    printf(" Пікова темп. Віна:    %.2f K (%.2f °C)\n", info->wien_temp_k, info->wien_temp_k - 273.15);
    printf(" Спектральний діапазон: %s\n", info->band_name);
    printf(" Біологічна дія:      %s\n", info->is_ionizing ? "[!] ІОНІЗУЮЧЕ (Руйнує хімічні зв'язки)" : "[OK] Неіонізуюче (Безпечно)");
    printf("==================================================\n");
}

int main(void) {
    printf("Розрахунок тестових сигналів ЕМ-спектра (Мова C):\n");

    /* Тест 1: Радіо FM 100 МГц */
    spectrum_info_t fm_radio = calculate_by_frequency(100.0e6);
    print_spectrum_card(&fm_radio);

    /* Тест 2: Мобільний Wi-Fi 2.45 ГГц */
    spectrum_info_t wifi = calculate_by_frequency(2.45e9);
    print_spectrum_card(&wifi);

    /* Тест 3: Зелений лазер 532 нм */
    spectrum_info_t green_laser = calculate_by_frequency(C_SPEED / 532.0e-9);
    print_spectrum_card(&green_laser);

    /* Тест 4: Медичний рентген 30 ЕГц (3e19 Гц) */
    spectrum_info_t xray = calculate_by_frequency(3.0e19);
    print_spectrum_card(&xray);

    return 0;
}
