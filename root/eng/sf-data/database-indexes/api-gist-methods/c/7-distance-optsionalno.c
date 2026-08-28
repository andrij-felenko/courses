#include "postgres.h"
#include "fmgr.h"
#include "access/gist.h"

/* Сигнатури експортованих C-функцій операторного класу GiST */

Datum my_gist_consistent(PG_FUNCTION_ARGS) {
    GISTENTRY *entry = (GISTENTRY *) PG_GETARG_POINTER(0);
    Datum query = PG_GETARG_DATUM(1);
    StrategyNumber strategy = (StrategyNumber) PG_GETARG_UINT16(2);
    bool *recheck = (bool *) PG_GETARG_POINTER(4);

    *recheck = false; /* Встановити true, якщо стиснення втратне */
    /* Обчислення перетину або вміщення предикату */
    PG_RETURN_BOOL(true);
}

Datum my_gist_union(PG_FUNCTION_ARGS) {
    GistEntryVector *entryvec = (GistEntryVector *) PG_GETARG_POINTER(0);
    int *sizep = (int *) PG_GETARG_POINTER(1);
    /* Обчислення спільного обмежувального прямокутника для всіх entryvec->vector */
    PG_RETURN_DATUM((Datum) 0);
}

Datum my_gist_penalty(PG_FUNCTION_ARGS) {
    GISTENTRY *origentry = (GISTENTRY *) PG_GETARG_POINTER(0);
    GISTENTRY *newentry = (GISTENTRY *) PG_GETARG_POINTER(1);
    float *penalty = (float *) PG_GETARG_POINTER(2);
    /* Penalty = Area(Union(orig, new)) - Area(orig) */
    *penalty = 0.0f;
    PG_RETURN_POINTER(penalty);
}

Datum my_gist_picksplit(PG_FUNCTION_ARGS) {
    GistEntryVector *entryvec = (GistEntryVector *) PG_GETARG_POINTER(0);
    GIST_SPLITVEC *v = (GIST_SPLITVEC *) PG_GETARG_POINTER(1);
    /* Квадратичний або лінійний поділ Гуттмана */
    PG_RETURN_POINTER(v);
}
