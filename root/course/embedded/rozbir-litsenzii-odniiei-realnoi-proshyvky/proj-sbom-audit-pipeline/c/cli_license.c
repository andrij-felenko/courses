/* cli_license.c — вивід ліцензійної таблиці з Flash у послідовну консоль.
 *
 * Формат навмисно колонковий: оператор читає його з термінала, а тестовий стенд
 * розбирає той самий вивід регулярним виразом і звіряє з паспортом SBOM.
 */
#include "cli_license.h"
#include "license_table.h"

#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define COL_NAME     26
#define COL_VERSION   9
#define COL_LICENSE  38
#define LINE_BUF    200

/* Шапку друкуємо готовим рядком, а не через "%-26s". Причина груба й практична:
 * printf рахує ширину в БАЙТАХ, а українська шапка в UTF-8 займає їх удвічі
 * більше, ніж символів, — колонки поїхали б рівно на довжину слова. Дані ж
 * у таблиці чисто ASCII, тому їх ширину рахувати можна. */
static const char *const k_header =
    "Компонент                  Версія    Ліцензія                              Правовласник\r\n";

static const char *const k_rule =
    "-------------------------- --------- -------------------------------------- ------------\r\n";

/* Обрізаємо задовге поле й ставимо крапку, щоб рядок не з'їхав. */
static void put_field(char *dst, size_t width, const char *text)
{
    size_t len = strlen(text);

    if (len > width) {
        memcpy(dst, text, width - 1);
        dst[width - 1] = '.';
    } else {
        memcpy(dst, text, len);
        memset(dst + len, ' ', width - len);
    }
}

static void print_row(const license_entry_t *entry, cli_out_fn out)
{
    char row[LINE_BUF];
    size_t pos = 0;

    put_field(row + pos, COL_NAME, entry->name);
    pos += COL_NAME;
    row[pos++] = ' ';

    put_field(row + pos, COL_VERSION, entry->version);
    pos += COL_VERSION;
    row[pos++] = ' ';

    put_field(row + pos, COL_LICENSE, entry->spdx);
    pos += COL_LICENSE;
    row[pos++] = ' ';

    /* Правовласник — останній, його не вирівнюємо: рядок і так закінчується. */
    size_t left = sizeof(row) - pos - 3;   /* \r \n \0 */
    size_t holder_len = strlen(entry->holder);
    if (holder_len > left) {
        holder_len = left;
    }
    memcpy(row + pos, entry->holder, holder_len);
    pos += holder_len;

    row[pos++] = '\r';
    row[pos++] = '\n';
    row[pos] = '\0';
    out(row);
}

static void print_card(const license_entry_t *entry, cli_out_fn out)
{
    out("\r\nКомпонент   : ");
    out(entry->name);
    out("\r\nВерсія      : ");
    out(entry->version);
    out("\r\nЛіцензія    : ");
    out(entry->spdx);
    out("\r\nПравовласник: ");
    out(entry->holder);
    out("\r\nЗастереження: ");
    out(entry->notice != NULL ? entry->notice : "окремих умов немає");
    out("\r\n\r\n");
}

cli_status_t cli_cmd_license(const char *args, cli_out_fn out)
{
    if (args != NULL && *args != '\0') {
        const license_entry_t *entry = license_table_find(args);
        if (entry == NULL) {
            out("\r\nкомпонента з такою назвою в образі немає; "
                "виконайте license без аргументів\r\n");
            return CLI_ERR_ARGS;
        }
        print_card(entry, out);
        return CLI_OK;
    }

    char footer[96];

    out("\r\n=== СКЛАД ПРОШИВКИ ТА ЛІЦЕНЗІЇ (SBOM) ===\r\n");
    out(k_header);
    out(k_rule);

    for (size_t i = 0; i < license_table_count; ++i) {
        print_row(&license_table[i], out);
    }

    out(k_rule);
    snprintf(footer, sizeof(footer),
             "Компонентів: %u. Подробиці: license <назва>.\r\n",
             (unsigned)license_table_count);
    out(footer);
    out("Повні тексти ліцензій — в інструкції користувача та за письмовим запитом.\r\n\r\n");
    return CLI_OK;
}

cli_status_t cli_cmd_about(const char *args, cli_out_fn out)
{
    (void)args;

    out("\r\nВиріб    : ");
    out(fw_product_name);
    out("\r\nПрошивка : ");
    out(fw_product_version);
    out("\r\nЗібрано  : " __DATE__ " " __TIME__);
    /* Хеш паспорта прив'язує консольну відповідь до підписаного метапакета OTA:
     * стенд звіряє цей рядок із serialNumber та hashes у firmware.cdx.json. */
    out("\r\nSBOM     : SHA-256 ");
    out(fw_sbom_sha256);
    out("\r\nСклад компонентів: команда license\r\n\r\n");
    return CLI_OK;
}
