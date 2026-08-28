#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <math.h>    // sinf, cosf, atan2f, sqrtf, fabsf

// ── Розмірності спільного стану ───────────────────────────────────────────
#define POSE_N   3                 // поза: x, y, theta
#define LM_MAX   30                // максимум орієнтирів у карті (фіксовано!)
#define DIM_MAX  (POSE_N + 2*LM_MAX)   // повна довжина вектора стану

// Спільна оцінка SLAM: ОДИН вектор стану + ОДНА матриця коваріації.
// Поточна довжина dim = 3 + 2*n_lm; решта буферів — про запас.
typedef struct {
    float x[DIM_MAX];                   // [x y theta | mx1 my1 mx2 my2 ...]
    float P[DIM_MAX][DIM_MAX];          // спільна коваріація (dim x dim)
    int   dim;                          // активна довжина = 3 + 2*n_lm
    int   n_lm;                         // скільки орієнтирів уже в карті
    int   lm_id[LM_MAX];                // зовнішній ідентифікатор орієнтира i
} Slam;

// Зручні «вікна» в стані: де лежить поза і де — i-й орієнтир.
static inline float *pose(Slam *s)        { return &s->x[0]; }       // 3 числа
static inline int    lm_off(int i)        { return POSE_N + 2*i; }   // зсув mx_i

void slam_init(Slam *s) {
    memset(s, 0, sizeof(*s));
    s->dim  = POSE_N;
    s->n_lm = 0;
    // Початкова невпевненість пози: ми оголошуємо старт початком координат
    // і знаємо його ТОЧНО (це наша система відліку) — тож майже нуль.
    s->P[0][0] = s->P[1][1] = 1e-6f;    // x, y
    s->P[2][2] = 1e-6f;                 // theta
}
