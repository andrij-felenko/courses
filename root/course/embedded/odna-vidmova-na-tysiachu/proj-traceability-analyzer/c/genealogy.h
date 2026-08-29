#ifndef GENEALOGY_H
#define GENEALOGY_H

#include <stddef.h>

#define NAME_LEN 24
#define MAX_PARTS 8

/* Скільки плат довкола стику котушок вважаємо непевними: у тракті подавача
   лишається 10-20 компонентів, яких сканер живильника вже не бачив. */
#define SPLICE_BOARDS 20

/* Походження одного компонента на платі: звідки автомат його взяв. */
typedef struct {
    char designator[NAME_LEN];   /* C12, U4, R28 */
    char reel_uid[NAME_LEN];     /* штрихкод котушки */
    char lot_code[NAME_LEN];     /* партія постачальника */
    char date_code[NAME_LEN];    /* код дати виготовлення чіпа */
    int  uncertain;              /* плата потрапила в зону склейки стрічок */
} PartOrigin;

typedef struct {
    char serial[NAME_LEN];
    char line[NAME_LEN];         /* SMT-лінія */
    char profile[NAME_LEN];      /* термопрофіль печі оплавлення */
    long long scan_time;         /* Unix-час сканування DataMatrix на вході лінії */
    PartOrigin parts[MAX_PARTS];
    int    part_count;
    int    failed;               /* є рекламація з поля */
    double ttf_hours;            /* напрацювання до відмови */
} Board;

typedef struct { Board *items; size_t count, cap; } BoardSet;

/* Вікно життя котушки в живильнику: [from_ts, to_ts) на конкретній лінії. */
typedef struct {
    char line[NAME_LEN], designator[NAME_LEN], reel_uid[NAME_LEN],
         lot_code[NAME_LEN], date_code[NAME_LEN];
    long long from_ts, to_ts;
    int spliced;                 /* перехід до наступної котушки зробили склейкою */
} FeederWindow;

typedef struct { FeederWindow *items; size_t count, cap; } FeederLog;

void  boards_init(BoardSet *s);
void  boards_free(BoardSet *s);
Board *boards_add(BoardSet *s);                       /* NULL при браку пам'яті */
Board *boards_find(BoardSet *s, const char *serial);

void  feeders_init(FeederLog *l);
void  feeders_free(FeederLog *l);
FeederWindow *feeders_add(FeederLog *l);

/* mes.csv:      serial,smt_line,reflow_profile,scan_epoch
   feeders.csv:  smt_line,designator,reel_uid,lot_code,date_code,from_epoch,to_epoch,spliced
   returns.csv:  serial,ttf_hours,symptom
   Повертають 0 або -1; текст помилки з номером рядка лягає в err. */
int load_mes(BoardSet *s, const char *path, char *err, size_t errlen);
int load_feeders(FeederLog *l, const char *path, char *err, size_t errlen);
int load_returns(BoardSet *s, const char *path, char *err, size_t errlen);

/* Зшивання генеалогії: кожній платі — котушки, що стояли на її лінії в мить
   сканування, плюс позначка непевності в зонах склейки. */
void join_genealogy(BoardSet *s, const FeederLog *l);

#endif /* GENEALOGY_H */
