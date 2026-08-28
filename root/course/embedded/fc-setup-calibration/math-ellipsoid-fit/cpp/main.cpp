#include <stdint.h>
#include <math.h>

#define GRAVITY_MSS   9.80665f     // еталон довжини: |виправлений вектор| має = g
#define NP            6            // параметрів: 3 зсуви + 3 масштаби (діагональна модель)

typedef struct { float x, y, z; } vec3_t;

// Параметри підгонки: зсуви o.{x,y,z} і масштаби d.{x,y,z}.
// Індексація p[0..5] = {oₓ,o_y,o_z, dₓ,d_y,d_z} — щоб зручно бігати циклом.
typedef struct {
    float o[3];   // зсуви
    float d[3];   // масштаби (діагональ M)
} ellip_param_t;

// Розв'язати малу симетричну систему A·x = b (NP×NP) методом Гаусса
// з вибором головного елемента. Повертає false, якщо матриця вироджена
// (погана геометрія вимірів → параметр невизначений).
static bool solve_linear(float A[NP][NP], float b[NP], float x[NP])
{
    for (int col = 0; col < NP; col++) {
        // вибір головного рядка — найбільший за модулем елемент стовпця
        int piv = col;
        for (int r = col + 1; r < NP; r++)
            if (fabsf(A[r][col]) > fabsf(A[piv][col])) piv = r;
        if (fabsf(A[piv][col]) < 1e-12f) return false;   // вироджена → не обернути

        // переставити рядки piv ↔ col (і в A, і в b)
        for (int c = 0; c < NP; c++) { float t = A[col][c]; A[col][c] = A[piv][c]; A[piv][c] = t; }
        { float t = b[col]; b[col] = b[piv]; b[piv] = t; }

        // виключити стовпець col з рядків нижче
        for (int r = col + 1; r < NP; r++) {
            float f = A[r][col] / A[col][col];
            for (int c = col; c < NP; c++) A[r][c] -= f * A[col][c];
            b[r] -= f * b[col];
        }
    }
    // зворотний хід
    for (int r = NP - 1; r >= 0; r--) {
        float s = b[r];
        for (int c = r + 1; c < NP; c++) s -= A[r][c] * x[c];
        x[r] = s / A[r][r];
    }
    return true;
}

// Одна ітерація Ґауса–Ньютона підгонки сфери.
// s[]  — n знятих сирих векторів;  par — поточні параметри (оновлюються на місці).
// Повертає норму кроку ‖Δp‖ (мала → зійшлося), або від'ємне при виродженні.
static float gauss_newton_step(const vec3_t s[], int n, ellip_param_t *par)
{
    float JtJ[NP][NP] = {{0}};   // Σ (стовпець якобіана)·(стовпець якобіана)ᵀ  — 6×6
    float Jte[NP]     = {0};     // −Σ (стовпець якобіана)·εᵢ                    — 6

    for (int i = 0; i < n; i++) {
        // виправлений вектор v = M·(sᵢ − o):  vₖ = dₖ·(sᵢₖ − oₖ)
        float diff[3] = { s[i].x - par->o[0], s[i].y - par->o[1], s[i].z - par->o[2] };
        float v[3]    = { par->d[0]*diff[0], par->d[1]*diff[1], par->d[2]*diff[2] };
        float norm    = sqrtf(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
        if (norm < 1e-6f) continue;                 // вироджений вимір — пропустити (не ділити на ~0)

        float eps = GRAVITY_MSS - norm;             // нев'язка цього виміру: g − ‖v‖

        // рядок якобіана J[i][*] = ∂εᵢ/∂p — виведені вище похідні:
        float row[NP];
        for (int k = 0; k < 3; k++) {
            row[k]     =  (par->d[k] * v[k]) / norm;         // ∂εᵢ/∂oₖ =  dₖ·vₖ/‖v‖
            row[3 + k] = -(v[k] * diff[k]) / norm;           // ∂εᵢ/∂dₖ = −vₖ·diffₖ/‖v‖
        }

        // накопичити внесок цього виміру в нормальні рівняння:
        //   JᵀJ += rowᵀ·row ;   −Jᵀε += −row·εᵢ
        for (int a = 0; a < NP; a++) {
            Jte[a] -= row[a] * eps;                          // права частина: −Jᵀε
            for (int c = 0; c < NP; c++)
                JtJ[a][c] += row[a] * row[c];                // матриця:        JᵀJ
        }
    }

    // розв'язати (JᵀJ)·Δp = −Jᵀε
    float dp[NP];
    if (!solve_linear(JtJ, Jte, dp)) return -1.0f;           // вироджено — геометрія бідна

    // оновити параметри p += Δp і заразом порахувати ‖Δp‖
    float step2 = 0.0f;
    for (int k = 0; k < 3; k++) {
        par->o[k] += dp[k];      step2 += dp[k]     * dp[k];
        par->d[k] += dp[3 + k];  step2 += dp[3 + k] * dp[3 + k];
    }
    return sqrtf(step2);          // норма кроку — критерій збіжності зовні
}
