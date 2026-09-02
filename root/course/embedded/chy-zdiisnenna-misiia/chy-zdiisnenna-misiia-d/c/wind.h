#ifndef WIND_H
#define WIND_H

#include <stdbool.h>

/* Прогноз вітру приходить із наземної метеостанції: швидкість на висоті
   анемометра. На висоті польоту вітер інший — його дає закон Гельмана. */
typedef struct {
    float speed_mps;        /* w0 — виміряна швидкість на висоті ref_height_m */
    float from_deg;         /* звідки дме: 0 — з півночі, 90 — зі сходу */
    float ref_height_m;     /* z0, зазвичай 10 м */
    float roughness_alpha;  /* alpha: 0.14 відкрите поле, 0.20...0.28 ліс і пагорби */
} WindProfile;

/* Розв'язок трикутника швидкостей для одного відрізка маршруту. */
typedef struct {
    float speed_mps;         /* вітер на висоті польоту */
    float along_mps;         /* уздовж лінії шляху: + попутний, - зустрічний */
    float cross_mps;         /* поперек: + зносить праворуч від лінії */
    float crab_deg;          /* кут зносу (краб-кут), який тримає автопілот */
    float ground_speed_mps;  /* поступ уздовж лінії шляху */
} LegWind;

float wind_at_height(const WindProfile *profile, float height_agl_m);

/* false — рівняння зносу не має дійсного розв'язку: боковий вітер
   перевищує повітряну швидкість, лінію шляху втримати неможливо. */
bool wind_solve_leg(const WindProfile *profile,
                    float track_deg,
                    float height_agl_m,
                    float airspeed_mps,
                    LegWind *out);

#endif /* WIND_H */
