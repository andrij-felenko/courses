#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_DIAGNOSTIC_ITEMS 24
#define NOISE_THRESHOLD_DPS 5.0f

/* Опис діагностичного прапорця Betaflight */
typedef struct {
    uint8_t bit_index;
    const char *name;
    const char *description;
    const char *action_required;
} bench_flag_def_t;

/* Реєстр прапорців блокування */
static const bench_flag_def_t BENCH_FLAGS[MAX_DIAGNOSTIC_ITEMS] = {
    {0,  "NO_GYRO",         "Апаратний збій давача гіроскопа на шині SPI", "Перевірити пайку IMU та стабілізатор 3.3V"},
    {1,  "FAILSAFE",        "Активний аварійний режим Failsafe",           "Увімкнути радіопульт, перевірити живлення RX"},
    {2,  "RX_FAILSAFE",     "Приймач повідомляє про втрату зв'язку",       "Відновити радіолінк передавача з приймачем"},
    {3,  "BAD_RX_RECOVERY", "Триває захисна затримка поновлення сигналу",  "Зачекати 1 секунду стабільного зв'язку"},
    {4,  "BOXFAILSAFE",     "Активовано AUX-перемикач аварійного Failsafe", "Опустити тумблер Failsafe на апаратурі"},
    {5,  "THROTTLE",        "Стік газу перевищує безпечний нуль (min_check)","Опустити стік газу в крайнє нижнє положення"},
    {6,  "CLI",             "Контролер утримується в режимі CLI термінала", "Ввести команду exit або закрити термінал"},
    {7,  "CMS_MENU",        "Відкрито конфігураційне OSD меню",             "Закрити екранне меню налаштування"},
    {8,  "OSD_MENU",        "Активне службове меню телеметрії",           "Вийти зі службового графічного інтерфейсу"},
    {9,  "ROLLPITCH_CLIP",  "Канали крену/тангажу за межами 1000..2000 мкс", "Відкалібрувати діапазони стіків на пульті"},
    {10, "SERVO_INIT",      "Триває калібрування сервоприводів",           "Дочекатися закінчення стартового тесту"},
    {11, "MOTOR_PROTOCOL",  "Конфлікт таймерів виходу або протоколу ESC",  "Перевірити вибір DShot та ресурсів таймерів"},
    {12, "ACC_CAL",         "Акселерометр не має збереженого калібрування","Провести 6-осьове калібрування акселерометра"},
    {13, "MOTOR_TEST",      "Увімкнено стендовий режим повзунків моторів",  "Вимкнути тестування моторів у конфігураторі"},
    {14, "ARM_SWITCH",      "Тумблер Arming увімкнено до старту плати",     "Перевести тумблер Arming у позицію Disarm"},
    {15, "MSP",             "USB-конфігуратор утримує монопольний зв'язок","Від'єднатися від конфігуратора"},
    {16, "PARALYZE",        "Активовано аварійний режим Crash Paralyze",    "Перезавантажити живлення польотного стека"},
    {17, "GPS",             "GPS-Rescue блокує старт без 3D Fix супутників","Зняти прапорець вимагання GPS для столу"},
    {18, "RESC",            "Активовано тумблер повернення додому",        "Вимкнути режим Rescue на пульті"},
    {19, "RPMFILTER",       "Відсутній зв'язок двостороннього DShot RPM",  "Подати живлення на ESC від силового акумулятора"},
    {20, "REBOOT_REQUIRED", "Змінені налаштування вимагають рестарту",      "Виконати команду save або reboot"},
    {21, "NOPREARM",        "Не активовано захисну клавішу Prearm",        "Затиснути запобіжний тумблер Prearm"},
    {22, "LOAD",            "Перевантаження ядра процесора (CPU > 75%)",   "Знизити частоту циклу PID loop"},
    {23, "CALIBRATING",     "Триває стартове усереднення нуля гіроскопа",  "Забезпечити нерухомість дрона на столі"}
};

/* Результати стендового аналізу */
typedef struct {
    uint32_t raw_mask;
    uint8_t active_count;
    bool is_arm_allowed;
} bench_diag_result_t;

/* Функція аналізу бітової маски */
bench_diag_result_t bench_decode_arming_mask(uint32_t mask) {
    bench_diag_result_t res;
    res.raw_mask = mask;
    res.active_count = 0;
    res.is_arm_allowed = (mask == 0);

    for (uint8_t i = 0; i < MAX_DIAGNOSTIC_ITEMS; ++i) {
        if ((mask & (1U << BENCH_FLAGS[i].bit_index)) != 0) {
            res.active_count++;
        }
    }
    return res;
}

/* Друк інженерного звіту */
void bench_print_report(const bench_diag_result_t *diag) {
    printf("\n=======================================================\n");
    printf("     СТЕНДОВИЙ ЗВІТ ГОТОВНОСТІ ДО АРМІНГУ (PRE-ARM)    \n");
    printf("=======================================================\n");
    printf("Бітова маска прапорців: 0x%08X\n", diag->raw_mask);

    if (diag->is_arm_allowed) {
        printf("СТАТУС: [ УСПІХ ] Усі блокування знято. Армінг дозволено.\n");
    } else {
        printf("СТАТУС: [ ЗАБЛОКОВАНО ] Виявлено активних перешкод: %d\n", diag->active_count);
        printf("-------------------------------------------------------\n");
        printf("Деталізація блокувань:\n");

        for (uint8_t i = 0; i < MAX_DIAGNOSTIC_ITEMS; ++i) {
            if ((diag->raw_mask & (1U << BENCH_FLAGS[i].bit_index)) != 0) {
                printf("  [!] Біт %2d: %-16s | %s\n",
                       BENCH_FLAGS[i].bit_index,
                       BENCH_FLAGS[i].name,
                       BENCH_FLAGS[i].description);
                printf("      ДІЯ: %s\n", BENCH_FLAGS[i].action_required);
            }
        }
    }
    printf("=======================================================\n\n");
}

/* Перевірка знака зворотного зв'язку PID (Negative Feedback Test) */
bool bench_verify_pid_negative_feedback(float gyro_rate_dps, float delta_motor_throttle) {
    if (gyro_rate_dps > NOISE_THRESHOLD_DPS && delta_motor_throttle > 0.01f) {
        return true; /* Від'ємний зворотний зв'язок працює правильно */
    }
    if (gyro_rate_dps < -NOISE_THRESHOLD_DPS && delta_motor_throttle < -0.01f) {
        return true;
    }
    return false;
}
