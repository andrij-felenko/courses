typedef enum { TENTATIVE, CONFIRMED, DELETED } TrackState;

typedef struct {
    int        id;            /* стійкий номер об'єкта */
    KF         kf;            /* фільтр Калмана зі станом цілі */
    TrackState state;
    int        hits;          /* скільки разів поспіль був збіг */
    int        misses;        /* скільки кадрів поспіль без детекції */
    int        age;           /* скільки кадрів живе всього */
} Track;

/* один кадр: tracks[] уже мають прогноз (predict зроблено),
   matched[i] = індекс детекції для треку i або -1 (без пари) */
void update_tracks(Track *tracks, int n, const Rect *dets, const int *matched,
                   int min_hits, int max_missed)
{
    for (int i = 0; i < n; i++) {
        Track *t = &tracks[i];
        t->age++;

        if (matched[i] >= 0) {                 /* є детекція → update фільтра */
            kf_update(&t->kf, dets[matched[i]]);
            t->hits++;
            t->misses = 0;
            if (t->state == TENTATIVE && t->hits >= min_hits)
                t->state = CONFIRMED;          /* проба витримала → підтверджено */
        } else {                                /* пари немає → ведемо наосліп */
            t->misses++;
            if (t->state == TENTATIVE)
                t->state = DELETED;            /* проба зірвалась одразу */
            else if (t->misses > max_missed)
                t->state = DELETED;            /* підтверджений жив, та зник надовго */
        }
    }
    /* (окремим проходом: викинути DELETED і завести нові TENTATIVE
        з детекцій, що лишились без пари — див. тему sort-tracking-algorithm) */
}
