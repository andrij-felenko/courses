#include <math.h>

// Доступна ємність (А·год) на струмі load_A з поправкою Пойкерта.
// cap_rated_Ah  — паспортна ємність
// i_rated_A     — струм, на якому виміряли паспорт (напр. C/20)
// k             — показник Пойкерта хімії (свинець ~1.3, літій ~1.05)
static float peukert_capacity_Ah(float cap_rated_Ah, float i_rated_A,
                                 float load_A, float k)
{
    if (load_A <= 0.0f) return cap_rated_Ah;      // без навантаження — увесь запас
    return cap_rated_Ah * powf(i_rated_A / load_A, k - 1.0f);
}

// Оцінка часу до відсічки (год) за сталого струму.
static float runtime_hours(float cap_rated_Ah, float i_rated_A,
                           float load_A, float k)
{
    float cap = peukert_capacity_Ah(cap_rated_Ah, i_rated_A, load_A, k);
    return cap / load_A;                           // а не cap_rated_Ah / load_A!
}
