#include <math.h>
#include <stdio.h>

// Стелі руху та повністю спланований профіль.
typedef struct {
    double j[7];                 // ривок у кожній із 7 фаз: +J,0,−J,0,−J,0,+J
    double t[8];                 // t[k] — момент КІНЦЯ фази k (t[0]=0)
    double a0[7], v0[7], x0[7];  // стан (a,v,x) на ПОЧАТКУ кожної фази
    double total;                // повна тривалість руху, с
    double reach;                // фактично досягнута пікова швидкість, м/с
} SCurve;

// Спланувати симетричний профіль спокій→спокій на відстань dist за стелями V,A,J.
// Заповнює *s. Повертає 1, якщо крейсерську V досягнуто, інакше 0 (хід закороткий).
int scurve_plan(SCurve *s, double dist, double V, double A, double J) {
    double Tj, Ta, Tv, vpk;
    int reached = 1;

    // (1) Чи встигає прискорення дорости до стелі A на шляху до крейсерської V?
    if (V * J >= A * A) {          // A²/J ≤ V — є плато прискорення
        Tj  = A / J;               // час наростання ривком від 0 до A
        Ta  = V / A - A / J;       // час утримання a = A (≥ 0)
        vpk = V;
    } else {                       // трикутне прискорення: пік < A
        Tj  = sqrt(V / J);
        Ta  = 0.0;
        vpk = V;
    }

    // (2) Відстань ОДНОГО розгінного сегмента. Профіль a(t) на розгоні симетричний
    //     відносно середини, тож крива v(t) точково-симетрична — її середнє рівно
    //     vpk/2, а отже d_розг = vpk·T_розг/2, де T_розг = 2·Tj + Ta.
    double d_acc    = vpk * (2.0 * Tj + Ta) / 2.0;
    double d_cruise = dist - 2.0 * d_acc;

    if (d_cruise >= 0.0) {
        Tv = d_cruise / vpk;       // крейсер триває, поки добираємо решту шляху
    } else {
        // (3) КОРОТКИЙ ХІД: до V не встигаємо. Крейсера нема (Tv=0), урізаємо пік.
        reached = 0;
        Tv = 0.0;
        double p = A * A / J;
        // Спроба A: прискорення все ще дістає A ⇒ vpk² + (A²/J)·vpk − A·dist = 0.
        vpk = (-p + sqrt(p * p + 4.0 * A * dist)) / 2.0;
        if (vpk >= p) {
            Tj = A / J;
            Ta = vpk / A - A / J;
        } else {
            // Спроба B: навіть без плато прискорення не дістає A — чистий трикутник:
            //   dist = 2·vpk^{3/2}/√J  ⇒  vpk = ∛(dist²·J / 4).
            vpk = cbrt(dist * dist * J / 4.0);
            Tj  = sqrt(vpk / J);
            Ta  = 0.0;
        }
    }

    // (4) Розкласти у таблицю 7 фаз і проінтегрувати сталим ривком крізь межі.
    const double dur[7] = { Tj, Ta, Tj, Tv, Tj, Ta, Tj };
    const double js[7]  = { +J, 0.0, -J, 0.0, -J, 0.0, +J };
    double a = 0.0, v = 0.0, x = 0.0;
    s->t[0] = 0.0;
    for (int k = 0; k < 7; k++) {
        double T = dur[k], jk = js[k];
        s->j[k]  = jk;
        s->a0[k] = a;  s->v0[k] = v;  s->x0[k] = x;   // стан на початку фази k
        // замкнені формули сталого ривка — точний стан у кінці фази:
        x += v * T + 0.5 * a * T * T + jk * T * T * T / 6.0;
        v += a * T + 0.5 * jk * T * T;
        a += jk * T;
        s->t[k + 1] = s->t[k] + T;
    }
    s->total = s->t[7];
    s->reach = vpk;
    return reached;
}
