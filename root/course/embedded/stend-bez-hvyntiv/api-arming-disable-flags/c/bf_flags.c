#include "bf_flags.h"

#include <string.h>

static const bf_flag_info_t k_flags[BF_FLAG_COUNT] = {
    [BF_NO_GYRO] = {"NO_GYRO",
        "гіроскоп не відповідає по шині SPI",
        "перевірити пайку модуля IMU і живлення 3.3 В"},
    [BF_FAILSAFE] = {"FAILSAFE",
        "активний режим Failsafe: валідних кадрів від приймача немає",
        "увімкнути передавач, перевірити живлення приймача"},
    [BF_RX_FAILSAFE] = {"RX_FAILSAFE",
        "приймач сам утримує власний прапорець failsafe",
        "відновити зв'язок пульта з радіомодулем (CRSF/ELRS/SBUS)"},
    [BF_BAD_RX_RECOVERY] = {"BAD_RX_RECOVERY",
        "лінк щойно повернувся, триває захисна секунда",
        "віднести пульт на 1.5-2 м від апарата й дочекатися чистої секунди"},
    [BF_BOXFAILSAFE] = {"BOXFAILSAFE",
        "AUX-канал переведений у зону аварійного Failsafe",
        "перевести тумблер Failsafe на пульті у вимкнений стан"},
    [BF_THROTTLE] = {"THROTTLE",
        "стік газу вище порога min_check",
        "опустити газ до кінця (1000 мкс) або відкалібрувати канал"},
    [BF_CLI] = {"CLI",
        "контролер у режимі командного рядка",
        "ввести exit або від'єднати термінал"},
    [BF_CMS_MENU] = {"CMS_MENU",
        "відкрито конфігураційне меню на OSD",
        "закрити меню пунктом Exit"},
    [BF_OSD_MENU] = {"OSD_MENU",
        "активний службовий екран телеметрії",
        "вийти з графічного режиму налаштування"},
    [BF_ROLLPITCH_CLIPPED] = {"ROLLPITCH_CLIPPED",
        "стіки крену/тангажу вийшли за діапазон каналу",
        "відкалібрувати кінцеві точки 1000-2000 мкс на пульті"},
    [BF_SERVO_INIT] = {"SERVO_INIT",
        "сервоприводи ще не зайняли нульове положення",
        "дочекатися завершення стартового позиціювання"},
    [BF_MOTOR_PROTOCOL] = {"MOTOR_PROTOCOL",
        "вибраний протокол ESC не лягає на таймери виходів",
        "перевірити конфігурацію DShot/PWM і ресурси таймерів"},
    [BF_ACC_CAL] = {"ACC_CAL",
        "акселерометр не має збережених калібрувальних коефіцієнтів",
        "провести калібрування на рівній поверхні"},
    [BF_MOTOR_TEST] = {"MOTOR_TEST",
        "увімкнено стендовий режим тестування двигунів",
        "вимкнути перемикач Enable motor testing у конфігураторі"},
    [BF_ARM_SWITCH] = {"ARM_SWITCH",
        "плату ввімкнено з уже піднятим тумблером Arming",
        "фізично опустити тумблер у стан Disarm"},
    [BF_MSP] = {"MSP",
        "конфігуратор утримує монопольний доступ",
        "закрити сесію GUI або від'єднати USB"},
    [BF_PARALYZE] = {"PARALYZE",
        "активовано режим повного блокування апарата",
        "перезавантажити контролер живленням"},
    [BF_GPS] = {"GPS",
        "немає 3D-фікса, а режим GPS-Rescue вимагає його для армінгу",
        "зняти вимогу GPS для армінгу або вийти на відкрите місце"},
    [BF_RESC] = {"RESC",
        "AUX-канал переведений у положення GPS-Rescue",
        "вимкнути тумблер повернення додому"},
    [BF_RPMFILTER] = {"RPMFILTER",
        "увімкнено RPM-фільтр, а регулятори не віддають телеметрію обертів",
        "живити ESC від силової батареї, а не лише від USB"},
    [BF_REBOOT_REQUIRED] = {"REBOOT_REQUIRED",
        "змінені параметри потребують перезавантаження",
        "надіслати save або перезапустити плату"},
    [BF_NOPREARM] = {"NOPREARM",
        "не затиснуто запобіжний перемикач Prearm",
        "затиснути Prearm перед тумблером Arm"},
    [BF_LOAD] = {"LOAD",
        "середнє завантаження процесора вище безпечного ліміту",
        "знизити частоту PID-циклу або перемкнути DShot600 на DShot300"},
    [BF_CALIBRATING] = {"CALIBRATING",
        "триває стартове калібрування гіроскопа",
        "покласти апарат нерухомо на 3-5 секунд"},
};

const bf_flag_info_t *bf_flag_info(bf_flag_t flag)
{
    if ((unsigned)flag >= BF_FLAG_COUNT) {
        return NULL;
    }
    return &k_flags[(unsigned)flag];
}

bool bf_flag_by_name(const char *name, size_t len, bf_flag_t *out)
{
    for (unsigned i = 0; i < BF_FLAG_COUNT; ++i) {
        if (strlen(k_flags[i].name) == len && strncmp(k_flags[i].name, name, len) == 0) {
            *out = (bf_flag_t)i;
            return true;
        }
    }
    return false;
}

static bool is_sep(char c)
{
    return c == ' ' || c == '\t' || c == ',' || c == '\r' || c == '\n';
}

uint32_t bf_parse_cli_status(const char *line, unsigned *unknown_count)
{
    static const char marker[] = "Arming disable flags:";

    uint32_t mask = 0;
    unsigned unknown = 0;

    const char *p = strstr(line, marker);
    p = (p != NULL) ? p + sizeof(marker) - 1 : line;

    while (*p != '\0') {
        while (*p != '\0' && is_sep(*p)) {
            ++p;
        }
        const char *start = p;
        while (*p != '\0' && !is_sep(*p)) {
            ++p;
        }
        const size_t len = (size_t)(p - start);
        if (len == 0) {
            break;
        }
        /* Чистий стан прошивка друкує словом None — це не назва прапорця. */
        if (len == 4 && strncmp(start, "None", 4) == 0) {
            continue;
        }
        bf_flag_t flag;
        if (bf_flag_by_name(start, len, &flag)) {
            mask |= BF_BIT(flag);
        } else {
            ++unknown;
        }
    }

    if (unknown_count != NULL) {
        *unknown_count = unknown;
    }
    return mask;
}

void bf_print_mask(uint32_t mask, FILE *out)
{
    if (mask == 0) {
        fprintf(out, "  маска чиста (0x00000000) — армінг дозволено\n");
        return;
    }

    for (unsigned bit = 0; bit < 32; ++bit) {
        if ((mask & ((uint32_t)1u << bit)) == 0) {
            continue;
        }
        const bf_flag_info_t *info = bf_flag_info((bf_flag_t)bit);
        if (info == NULL) {
            fprintf(out, "  біт %2u  <прошивка новіша за довідник>\n", bit);
            continue;
        }
        fprintf(out, "  біт %2u  %-18s %s\n", bit, info->name, info->cause);
        fprintf(out, "           рецепт: %s\n", info->remedy);
    }
}
