#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

#define MAX_RECORDS 25000
#define MAX_STR_LEN 64

typedef struct {
    char serial[MAX_STR_LEN];
    char smt_line[MAX_STR_LEN];
    char mcu_datecode[MAX_STR_LEN];
    char ldo_reel[MAX_STR_LEN];
    char mlcc_lot[MAX_STR_LEN];
    bool is_failed;
} BoardRecord;

typedef struct {
    char attr_name[MAX_STR_LEN];
    char attr_value[MAX_STR_LEN];
    int a; // фактор є + відмова
    int b; // фактор є + справний
    int c; // фактора нема + відмова
    int d; // фактора нема + справний
    double odds_ratio;
    double ci_low;
    double ci_high;
    double p_value;
} ContingencyResult;

static double log_factorial(int n) {
    return lgamma((double)(n + 1));
}

static double fisher_exact_2x2(int a, int b, int c, int d) {
    int n1 = a + b;
    int n0 = c + d;
    int m1 = a + c;
    int m0 = b + d;
    int total = n1 + n0;

    double log_hyper_denom = log_factorial(n1) + log_factorial(n0) +
                             log_factorial(m1) + log_factorial(m0) -
                             log_factorial(total);

    double log_p_observed = log_hyper_denom - (log_factorial(a) + log_factorial(b) +
                                              log_factorial(c) + log_factorial(d));
    double p_observed = exp(log_p_observed);

    int min_a = (m1 - n0 > 0) ? m1 - n0 : 0;
    int max_a = (n1 < m1) ? n1 : m1;

    double p_total = 0.0;
    for (int x = min_a; x <= max_a; ++x) {
        int cur_b = n1 - x;
        int cur_c = m1 - x;
        int cur_d = n0 - cur_c;

        double log_p_cur = log_hyper_denom - (log_factorial(x) + log_factorial(cur_b) +
                                              log_factorial(cur_c) + log_factorial(cur_d));
        double p_cur = exp(log_p_cur);

        if (p_cur <= p_observed * (1.0 + 1e-9)) {
            p_total += p_cur;
        }
    }
    return (p_total > 1.0) ? 1.0 : p_total;
}

static void calculate_metrics(ContingencyResult *res) {
    double a = res->a;
    double b = res->b;
    double c = res->c;
    double d = res->d;

    // Корекція Холдейна-Енскомба при нульових клітинках
    if (a == 0 || b == 0 || c == 0 || d == 0) {
        a += 0.5; b += 0.5; c += 0.5; d += 0.5;
    }

    res->odds_ratio = (a * d) / (b * c);
    double se_ln_or = sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d);
    double ln_or = log(res->odds_ratio);

    res->ci_low = exp(ln_or - 1.96 * se_ln_or);
    res->ci_high = exp(ln_or + 1.96 * se_ln_or);
    res->p_value = fisher_exact_2x2(res->a, res->b, res->c, res->d);
}

int main(void) {
    printf("=== Аналізатор виробничої генеалогії PCBA (C99) ===\n");

    int total_records = 20000;
    BoardRecord *records = calloc((size_t)total_records, sizeof(BoardRecord));
    if (!records) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    // Генерація виробничого випуску 20 000 плат
    for (int i = 0; i < total_records; ++i) {
        snprintf(records[i].serial, MAX_STR_LEN, "SN%05d", i + 1);
        snprintf(records[i].smt_line, MAX_STR_LEN, (i % 2 == 0) ? "Line-1" : "Line-2");
        snprintf(records[i].mcu_datecode, MAX_STR_LEN, (i < 10000) ? "DC2130" : "DC2134");
        snprintf(records[i].ldo_reel, MAX_STR_LEN, (i < 15000) ? "R-101" : "R-102");

        // Дефектний лот конденсаторів встановлений на платах SN14000..SN14999 (1000 шт)
        if (i >= 14000 && i < 15000) {
            strncpy(records[i].mlcc_lot, "L-8921", MAX_STR_LEN);
            // 1.8% відмов у дефектному лоті (18 штук)
            records[i].is_failed = (i % 55 == 0 && i < 14990);
        } else {
            strncpy(records[i].mlcc_lot, "L-4410", MAX_STR_LEN);
            // Фоновий брак у решті партій: 2 штуки на 19 000 плат (0.01%)
            records[i].is_failed = (i == 2500 || i == 8700);
        }
    }

    // Перевірка підозрілого атрибута MLCC Lot = L-8921
    ContingencyResult test_mlcc = {0};
    strncpy(test_mlcc.attr_name, "MLCC_Lot", MAX_STR_LEN);
    strncpy(test_mlcc.attr_value, "L-8921", MAX_STR_LEN);

    for (int i = 0; i < total_records; ++i) {
        bool match = (strcmp(records[i].mlcc_lot, "L-8921") == 0);
        if (match && records[i].is_failed) test_mlcc.a++;
        else if (match && !records[i].is_failed) test_mlcc.b++;
        else if (!match && records[i].is_failed) test_mlcc.c++;
        else if (!match && !records[i].is_failed) test_mlcc.d++;
    }

    calculate_metrics(&test_mlcc);

    printf("\nРезультати аналізу для [%s = %s]:\n", test_mlcc.attr_name, test_mlcc.attr_value);
    printf("  Клітинки матриці 2x2: a=%d, b=%d, c=%d, d=%d\n",
           test_mlcc.a, test_mlcc.b, test_mlcc.c, test_mlcc.d);
    printf("  Частота браку в групі:   %.3f%%\n", (double)test_mlcc.a / (test_mlcc.a + test_mlcc.b) * 100.0);
    printf("  Частота браку в контролі: %.4f%%\n", (double)test_mlcc.c / (test_mlcc.c + test_mlcc.d) * 100.0);
    printf("  Відношення шансів (OR):   %.2f (95%% CI: [%.2f .. %.2f])\n",
           test_mlcc.odds_ratio, test_mlcc.ci_low, test_mlcc.ci_high);
    printf("  Точний тест Фішера (p):   %.4e\n", test_mlcc.p_value);

    if (test_mlcc.p_value < 1e-5 && test_mlcc.odds_ratio > 10.0) {
        printf("\n[УВАГА] Виявлено статистично достовірне джерело браку!\n");
        printf("Ізоляція партії: вилучити зі складів плати з атрибутом %s=%s\n",
               test_mlcc.attr_name, test_mlcc.attr_value);
        printf("Діапазон серійних номерів для карантину: SN14001 .. SN15000\n");
    }

    free(records);
    return 0;
}
