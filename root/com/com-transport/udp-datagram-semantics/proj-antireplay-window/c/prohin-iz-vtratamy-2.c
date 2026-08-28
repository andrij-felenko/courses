#include <stdio.h>
#include <assert.h>

int main(void)
{
    /* Відправник слав 1…200 поспіль. Мережа зробила з цього таке:
       4 обігнала 3; 4 прилетіла двічі; 7 обігнала 6; 12 обігнала 9 і 5;
       далі величезний стрибок на 200, а останньою — давно списана 5. */
    static const uint32_t wire[] = {
        1, 2, 4, 3, 4, 7, 6, 12, 9, 5, 200, 5
    };

    arw w;
    arw_init(&w);
    for (size_t i = 0; i < sizeof wire / sizeof wire[0]; i++)
        arw_update(&w, wire[i]);
    arw_flush(&w);

    printf("прийнято %llu, втрачено %llu, дублів %llu, "
           "перестановок %llu, надто старих %llu\n",
           (unsigned long long)w.accepted,  (unsigned long long)w.lost,
           (unsigned long long)w.duplicate, (unsigned long long)w.reordered,
           (unsigned long long)w.too_old);

    assert(w.accepted  == 10);   /* 1,2,3,4,5,6,7,9,12,200 */
    assert(w.duplicate == 1);    /* друга четвірка */
    assert(w.reordered == 4);    /* 3, 6, 9 і 5 прийшли після новіших */
    assert(w.too_old   == 1);    /* остання п'ятірка — уже поза вікном */
    assert(w.lost      == 190);

    /* Головна перевірка: рахунок мусить зійтися до одиниці.
       Від найменшого баченого номера до найбільшого — 200 номерів,
       і кожен із них або прийнятий, або визнаний утраченим. */
    assert(w.accepted + w.lost == 200);
    return 0;
}
