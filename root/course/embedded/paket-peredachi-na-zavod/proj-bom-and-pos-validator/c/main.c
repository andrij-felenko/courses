#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_LINE_LEN   1024
#define MAX_ITEMS      2048
#define MAX_NAME_LEN   32

typedef struct {
    char name[MAX_NAME_LEN];
    char mpN[64];
    int  dnp;
    int  matched_in_cpl;
} BomEntry;

typedef struct {
    char name[MAX_NAME_LEN];
    double x;
    double y;
    double rot;
    char layer[16];
    int  matched_in_bom;
} CplEntry;

static void trim(char *s) {
    char *p = s;
    while (isspace((unsigned char)*p)) p++;
    if (p != s) memmove(s, p, strlen(p) + 1);
    size_t len = strlen(s);
    while (len > 0 && (isspace((unsigned char)s[len - 1]) || s[len - 1] == '\r' || s[len - 1] == '\n')) {
        s[--len] = '\0';
    }
}

static int parse_bom(const char *path, BomEntry *bom, int max_bom, int *bom_count) {
    FILE *f = fopen(path, "r");
    if (!f) {
        perror("Не вдалося відкрити BOM файл");
        return -1;
    }

    char line[MAX_LINE_LEN];
    int count = 0;
    int line_num = 0;

    while (fgets(line, sizeof(line), f)) {
        line_num++;
        trim(line);
        if (line_num == 1 || strlen(line) == 0) continue; // Пропуск заголовка

        char *token = strtok(line, ",;");
        if (!token) continue;
        char des_field[256];
        strncpy(des_field, token, sizeof(des_field) - 1);
        des_field[sizeof(des_field) - 1] = '\0';

        char *mpn_tok = strtok(NULL, ",;");
        char *pkg_tok = strtok(NULL, ",;");
        (void)pkg_tok;
        char *dnp_tok = strtok(NULL, ",;");

        int is_dnp = (dnp_tok && (strcmp(dnp_tok, "1") == 0 || strcasecmp(dnp_tok, "DNP") == 0));

        // Розбиваємо можливі списки референсів (напр. "C1 C2 C3" або "R1,R2")
        char *sub = strtok(des_field, " ,");
        while (sub) {
            trim(sub);
            if (strlen(sub) > 0 && count < max_bom) {
                strncpy(bom[count].name, sub, MAX_NAME_LEN - 1);
                bom[count].name[MAX_NAME_LEN - 1] = '\0';
                strncpy(bom[count].mpN, mpn_tok ? mpn_tok : "UNKNOWN", 63);
                bom[count].mpN[63] = '\0';
                bom[count].dnp = is_dnp;
                bom[count].matched_in_cpl = 0;
                count++;
            }
            sub = strtok(NULL, " ,");
        }
    }

    fclose(f);
    *bom_count = count;
    return 0;
}

static int parse_cpl(const char *path, CplEntry *cpl, int max_cpl, int *cpl_count) {
    FILE *f = fopen(path, "r");
    if (!f) {
        perror("Не вдалося відкрити CPL файл");
        return -1;
    }

    char line[MAX_LINE_LEN];
    int count = 0;
    int line_num = 0;

    while (fgets(line, sizeof(line), f)) {
        line_num++;
        trim(line);
        if (line_num == 1 || strlen(line) == 0) continue; // Пропуск заголовка

        char *des = strtok(line, ",;");
        char *xs = strtok(NULL, ",;");
        char *ys = strtok(NULL, ",;");
        char *rs = strtok(NULL, ",;");
        char *lay = strtok(NULL, ",;");

        if (des && xs && ys && rs && count < max_cpl) {
            trim(des);
            strncpy(cpl[count].name, des, MAX_NAME_LEN - 1);
            cpl[count].name[MAX_NAME_LEN - 1] = '\0';
            cpl[count].x = atof(xs);
            cpl[count].y = atof(ys);
            cpl[count].rot = atof(rs);
            strncpy(cpl[count].layer, lay ? lay : "Top", 15);
            cpl[count].matched_in_bom = 0;
            count++;
        }
    }

    fclose(f);
    *cpl_count = count;
    return 0;
}

int main(int argc, char **argv) {
    const char *bom_path = (argc > 1) ? argv[1] : "bom.csv";
    const char *cpl_path = (argc > 2) ? argv[2] : "cpl.csv";

    static BomEntry bom[MAX_ITEMS];
    static CplEntry cpl[MAX_ITEMS];
    int bom_count = 0, cpl_count = 0;

    if (parse_bom(bom_path, bom, MAX_ITEMS, &bom_count) != 0) return 2;
    if (parse_cpl(cpl_path, cpl, MAX_ITEMS, &cpl_count) != 0) return 2;

    int errors = 0;
    int warnings = 0;

    printf("=== ВАЛІДАЦІЯ ВИРОБНИЧОГО ПАКЕТА: BOM vs CPL ===\n");
    printf("Зчитано позицій: BOM=%d, CPL=%d\n\n", bom_count, cpl_count);

    // 1. Зіставлення BOM -> CPL
    for (int i = 0; i < bom_count; i++) {
        for (int j = 0; j < cpl_count; j++) {
            if (strcasecmp(bom[i].name, cpl[j].name) == 0) {
                bom[i].matched_in_cpl = 1;
                cpl[j].matched_in_bom = 1;
                if (bom[i].dnp) {
                    printf("[УВАГА / DNP] %s позначений як DNP у BOM, але знайдений у CPL (X=%.2f, Y=%.2f)\n",
                           bom[i].name, cpl[j].x, cpl[j].y);
                    warnings++;
                }
                break;
            }
        }
        if (!bom[i].matched_in_cpl && !bom[i].dnp) {
            printf("[ПОМИЛКА] %s (%s) є у BOM, але ВІДСУТНІЙ у Pick-and-Place файлі!\n",
                   bom[i].name, bom[i].mpN);
            errors++;
        }
    }

    // 2. Зіставлення CPL -> BOM (зайві компоненти на платі)
    for (int j = 0; j < cpl_count; j++) {
        if (!cpl[j].matched_in_bom) {
            printf("[ПОМИЛКА] %s є у CPL файлі (X=%.2f, Y=%.2f), але ВІДСУТНІЙ у відомості матеріалів BOM!\n",
                   cpl[j].name, cpl[j].x, cpl[j].y);
            errors++;
        }
    }

    printf("\nПідсумок: помилок=%d, зауважень=%d\n", errors, warnings);
    if (errors > 0) {
        printf("СТАТУС: ВІДХИЛЕНО. Пакет містить критичні розбіжності!\n");
        return 1;
    }

    printf("СТАТУС: УСПІШНО. Виробничі файли узгоджені.\n");
    return 0;
}
