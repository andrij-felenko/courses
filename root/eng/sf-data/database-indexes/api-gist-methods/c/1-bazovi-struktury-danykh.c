#include "postgres.h"
#include "access/gist.h"
#include "access/itup.h"

/* Запис елемента індексу GiST у C API */
typedef struct GISTENTRY {
    Datum       key;        /* Значення ключа або обмежувальний предикат (наприклад, BOX) */
    Relation    rel;        /* Дескриптор індексованої таблиці каталогу */
    Page        page;       /* Вказівник на дискову сторінку в буферному пулі */
    OffsetNumber offset;    /* Порядковий номер кортежу на сторінці (Line Pointer) */
    bool        leafkey;    /* true, якщо запис розміщений у листовому вузлі */
    bool        is_null;    /* true, якщо значення індексованого стовпця є NULL */
} GISTENTRY;

/* Вектор елементів сторінки для операцій Union та PickSplit */
typedef struct GistEntryVector {
    int32       n;          /* Кількість елементів у масиві */
    GISTENTRY   vector[FLEXIBLE_ARRAY_MEMBER];
} GistEntryVector;

/* Результат розщеплення сторінки: розподіл записів між двома сторінками */
typedef struct GIST_SPLITVEC {
    OffsetNumber *spl_left;       /* Масив зсувів кортежів для лівої нової сторінки */
    int           spl_nleft;      /* Кількість елементів ліворуч */
    Datum         spl_ldatum;     /* Об'єднаний узагальнювальний ключ (Union) лівої сторінки */

    OffsetNumber *spl_right;      /* Масив зсувів кортежів для правої нової сторінки */
    int           spl_nright;     /* Кількість елементів праворуч */
    Datum         spl_rdatum;     /* Об'єднаний узагальнювальний ключ (Union) правої сторінки */
} GIST_SPLITVEC;
