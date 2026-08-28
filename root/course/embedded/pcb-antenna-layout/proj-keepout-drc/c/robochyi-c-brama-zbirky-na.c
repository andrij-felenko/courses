#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Назва правила з .kicad_dru — за нею впізнаємо КРИТИЧНІ порушення keep-out.
// Має дослівно збігатися з (rule "...") у файлі правил.
#define ANT_RULE_NAME  "no copper in antenna keepout"

// Лічильник скільки разів підрядок needle трапився у тексті hay.
// Звичайний прохід вікном; повертає кількість НЕперекривних збігів.
static int count_substr(const char *hay, const char *needle) {
    int n = 0;
    size_t nlen = strlen(needle);
    if (nlen == 0) return 0;
    for (const char *p = hay; (p = strstr(p, needle)) != NULL; p += nlen)
        n++;
    return n;
}

// Прочитати весь файл у буфер (звіт DRC малий — кілька КБ навіть на щільній
// платі, тож читаємо цілком; для гігабайтних файлів так робити не можна).
static char *read_whole_file(const char *path, long *out_len) {
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return NULL; }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (len < 0) { fclose(f); return NULL; }
    char *buf = malloc((size_t)len + 1);
    if (!buf) { fclose(f); fprintf(stderr, "брак пам'яті\n"); return NULL; }
    size_t got = fread(buf, 1, (size_t)len, f);
    fclose(f);
    buf[got] = '\0';          // вузол: гарантуємо нуль-термінатор для strstr
    if (out_len) *out_len = (long)got;
    return buf;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "вжиток: %s drc.json\n", argv[0]);
        return 2;                          // 2 — помилка виклику, не плати
    }

    long len = 0;
    char *report = read_whole_file(argv[1], &len);
    if (!report) return 2;

    // Скільки порушень саме НАШОГО правила keep-out антени?
    int ant_viol = count_substr(report, ANT_RULE_NAME);

    // Груба оцінка ВСІХ порушень: KiCad у JSON виставляє "severity": "error".
    // (Для точного числа потрібен справжній парсер — див. пастки нижче.)
    int all_errors = count_substr(report, "\"severity\": \"error\"");

    free(report);

    printf("DRC: усього помилок=%d, з них keep-out антени=%d\n",
           all_errors, ant_viol);

    if (ant_viol > 0) {
        fprintf(stderr,
            "ЗБІРКУ СПИНЕНО: %d порушень keep-out антени.\n"
            "Під меандром або в зоні ANT_KEEPOUT є мідь — імовірно\n"
            "заливка землі на ВНУТРІШНЬОМУ шарі. Прибери мідь із зони.\n",
            ant_viol);
        return 1;                          // 1 — критично: зрив радіотракту
    }
    if (all_errors > 0) {
        fprintf(stderr,
            "Увага: %d інших порушень DRC (не keep-out). Перевір звіт.\n",
            all_errors);
        return 1;                          // теж валимо збірку, але іншим текстом
    }

    printf("DRC чисто: міді в зоні антени немає на жодному шарі.\n");
    return 0;                              // 0 — конвеєр пускає далі
}
