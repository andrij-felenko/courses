#define MAX_POINTS 32

extern double ref_time_seconds(void);   // мітка точного джерела (GPS/NTP), с
extern double own_time_seconds(void);   // власний час пристрою (з кварцу), с
extern void   wait_one_hour(void);      // довгий проміжок між звірками

// Метод B — похибка як нахил накопиченої різниці Δt(t).
double measure_ppm_accumulate(void)
{
    double t[MAX_POINTS], dt[MAX_POINTS];
    int n;

    for (n = 0; n < MAX_POINTS; n++) {
        wait_one_hour();                    // терпляче чекання між точками
        double ref = ref_time_seconds();
        double own = own_time_seconds();
        t[n]  = ref;                        // час спостереження (опорний)
        dt[n] = own - ref;                  // накопичена різниця, с
    }

    // Нахил прямої Δt = a·t + b (найменші квадрати): a — секунди на секунду.
    double st = 0, sdt = 0, stt = 0, stdt = 0;
    for (int i = 0; i < n; i++) {
        st   += t[i];
        sdt  += dt[i];
        stt  += t[i] * t[i];
        stdt += t[i] * dt[i];
    }
    double slope = ((double)n * stdt - st * sdt)
                 / ((double)n * stt  - st * st);

    return slope * 1e6;   // ppm; +вгору — власний кварц спішить
}
