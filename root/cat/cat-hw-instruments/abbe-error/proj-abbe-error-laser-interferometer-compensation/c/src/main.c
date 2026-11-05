#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "abbe_error.h"
#include "compensation_table.h"

static void print_usage(const char *prog_name) {
    printf("Використання: %s -i <вхідний_файл> [опції]\n\n", prog_name);
    printf("Опції:\n");
    printf("  -i <файл>      Шлях до файлу кутових вимірів інтерферометра (обов'язково)\n");
    printf("  -y <мм>        Горизонтальне плече Аббе dy (за замовчуванням: 0.0 мм)\n");
    printf("  -z <мм>        Вертикальне плече Аббе dz (за замовчуванням: 0.0 мм)\n");
    printf("  -u <одиниці>   Одиниці вимірювання кутів: arcsec, urad, mrad, rad (за замовчуванням: arcsec)\n");
    printf("  -o <файл>      Шлях для експорту таблиці корекцій у форматі CSV\n");
    printf("  -c <файл>      Шлях для експорту таблиці компенсації кроку для ЧПУ\n");
    printf("  -a <вісь>      Назва осі позиціонування (за замовчуванням: X)\n");
    printf("  -h, --help     Показати цю довідку та вийти\n\n");
    printf("Формат вхідного файлу вимірів (стовпці розділені пробілом або комою):\n");
    printf("  # Позиція_X_мм    Pitch    Yaw\n");
    printf("  0.0               1.20    -0.80\n");
    printf("  50.0              2.50    -1.10\n");
    printf("  100.0             3.10    -0.40\n");
}

int main(int argc, char *argv[]) {
    const char *input_path  = NULL;
    const char *csv_path    = NULL;
    const char *cnc_path    = NULL;
    const char *axis_name   = "X";
    abbe_arm_t  arm         = { 0.0, 0.0 };
    angle_unit_t unit       = ANGLE_UNIT_ARCSEC;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            return 0;
        } else if (strcmp(argv[i], "-i") == 0 && i + 1 < argc) {
            input_path = argv[++i];
        } else if (strcmp(argv[i], "-y") == 0 && i + 1 < argc) {
            arm.dy = atof(argv[++i]);
        } else if (strcmp(argv[i], "-z") == 0 && i + 1 < argc) {
            arm.dz = atof(argv[++i]);
        } else if (strcmp(argv[i], "-u") == 0 && i + 1 < argc) {
            if (!abbe_parse_unit(argv[++i], &unit)) {
                fprintf(stderr, "Помилка: невідома кутова одиниця вимірювання '%s'.\n", argv[i]);
                fprintf(stderr, "Допустимі варіанти: arcsec, urad, mrad, rad.\n");
                return 1;
            }
        } else if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            csv_path = argv[++i];
        } else if (strcmp(argv[i], "-c") == 0 && i + 1 < argc) {
            cnc_path = argv[++i];
        } else if (strcmp(argv[i], "-a") == 0 && i + 1 < argc) {
            axis_name = argv[++i];
        } else {
            fprintf(stderr, "Помилка: невідомий або некоректний аргумент '%s'.\n", argv[i]);
            print_usage(argv[0]);
            return 1;
        }
    }

    if (!input_path) {
        fprintf(stderr, "Помилка: не вказано вхідний файл кутових вимірювань (-i <файл>).\n\n");
        print_usage(argv[0]);
        return 1;
    }

    /* Ініціалізація та завантаження профілю вимірів */
    compensation_table_t table;
    if (!comp_table_init(&table, &arm, unit)) {
        fprintf(stderr, "Помилка: не вдалося виділити ресурси для таблиці компенсації.\n");
        return 1;
    }

    if (!comp_table_load_file(&table, input_path)) {
        fprintf(stderr, "Помилка: не вдалося зчитати дані з файлу '%s' або недостатньо точок (мінімум 2).\n", input_path);
        comp_table_free(&table);
        return 1;
    }

    /* Валідація кроку та монотонності координат */
    if (!comp_table_validate(&table)) {
        fprintf(stderr, "Помилка валідації: позиції осі повинні бути впорядковані за суворим зростанням.\n");
        comp_table_free(&table);
        return 1;
    }

    /* Обчислення похибки Аббе та компенсуючих поправок */
    if (!comp_table_compute(&table)) {
        fprintf(stderr, "Помилка: не вдалося провести математичний розрахунок похибки Аббе.\n");
        comp_table_free(&table);
        return 1;
    }

    /* Експорт у CSV за вимогою користувача */
    if (csv_path) {
        if (comp_table_export_csv(&table, csv_path)) {
            printf("[OK] Таблицю корекцій CSV збережено у: %s\n", csv_path);
        } else {
            fprintf(stderr, "Помилка під час запису CSV-файлу: %s\n", csv_path);
        }
    }

    /* Експорт у формат ЧПУ за вимогою користувача */
    if (cnc_path) {
        if (comp_table_export_cnc(&table, cnc_path, axis_name)) {
            printf("[OK] Таблицю компенсації кроку ЧПУ збережено у: %s\n", cnc_path);
        } else {
            fprintf(stderr, "Помилка під час запису файлу ЧПУ: %s\n", cnc_path);
        }
    }

    /* Розрахунок метрологічних характеристик та виведення зведеного звіту */
    compensation_stats_t stats;
    if (comp_table_get_stats(&table, &stats)) {
        printf("\n================================================================================\n");
        printf("       ЗВЕДЕНИЙ ЗВІТ РОЗРАХУНКУ ПОХИБКИ АББЕ ДЛЯ ОСІ %s\n", axis_name);
        printf("================================================================================\n");
        printf("Конфігурація просторового плеча Аббе:\n");
        printf("  - Горизонтальне зміщення (dy):  %10.3f мм\n", arm.dy);
        printf("  - Вертикальне зміщення (dz):    %10.3f мм\n", arm.dz);
        printf("  - Одиниця вхідних кутів:        %s\n", abbe_unit_to_string(unit));
        printf("\nПараметри робочого ходу осі:\n");
        printf("  - Кількість точок вимірювання:  %zu\n", stats.count);
        printf("  - Діапазон переміщення:         від %.3f мм до %.3f мм\n", stats.start_pos_mm, stats.end_pos_mm);
        printf("  - Номінальний крок позицій:     %10.3f мм\n", stats.step_mm);
        printf("\nМетрологічний аналіз похибок першого порядку:\n");
        printf("  - Мінімальна похибка Аббе:      %10.3f мкм (%.6f мм)\n", stats.min_error_um, stats.min_error_um / 1000.0);
        printf("  - Максимальна похибка Аббе:     %10.3f мкм (%.6f мм)\n", stats.max_error_um, stats.max_error_um / 1000.0);
        printf("  - Розмах похибки (Peak-to-Peak):%10.3f мкм (%.6f мм)\n", stats.peak_to_peak_um, stats.peak_to_peak_um / 1000.0);
        printf("  - Максимальна модуль-поправка:  %10.3f мкм (%.6f мм)\n", stats.max_correction_um, stats.max_correction_um / 1000.0);
        printf("================================================================================\n");
    }

    comp_table_free(&table);
    return 0;
}
