/* socktune.h */
#ifndef SOCKTUNE_H
#define SOCKTUNE_H

typedef enum {
    SOCK_PROFILE_LATENCY,      /* дрібне й негайно: керування, запит-відповідь */
    SOCK_PROFILE_THROUGHPUT    /* великий потік: передача файлів, вивантаження */
} sock_profile;

/* Що ми знаємо про канал. Без цих двох чисел розмір буфера не обчислити,
   тож покажчик на неї дозволено лишити NULL — і тоді буфери НЕ чіпаємо. */
typedef struct {
    double mbit_per_s;         /* пропускна здатність вузького місця */
    double rtt_ms;             /* час обігу — виміряний, не з паспорта */
} sock_link;

typedef enum {
    OPT_OK,            /* ядро взяло те, що просили */
    OPT_CHANGED,       /* узяло, але дало інше число: стеля, округлення */
    OPT_UNSUPPORTED,   /* опції тут немає — інший стек, інша система */
    OPT_FAILED         /* справжня помилка */
} opt_state;

typedef struct {
    const char *name;
    long        want;
    long        got;
    opt_state   state;
    int         err;   /* errno, якщо він був */
} opt_result;

#define SOCK_REPORT_CAP 16

typedef struct {
    opt_result item[SOCK_REPORT_CAP];
    int n;             /* заповнених рядків */
    int overflow;      /* не вмістилося; має бути 0 — це сторожок на майбутнє */
    int too_late;      /* сокет уже з'єднаний або слухає: буфери пропущено */
    int changed, unsupported, failed;
} sock_report;

int  sock_apply_profile(int fd, sock_profile p, const sock_link *link,
                        sock_report *rep);
void sock_report_print(const sock_report *rep);
long sock_bdp_bytes(double mbit_per_s, double rtt_ms);

#endif
