#ifndef CALIB6_H
#define CALIB6_H

#include "linalg.h"

/* Скільки параметрів шукаємо. Статичні дані бачать лише MᵀM, тому за представника
   класу беремо нижню трикутну M: вона єдина з додатною діагоналлю.
   Обертальну частину (R_align відносно тіла) статика не спостерігає взагалі —
   її дає механічне пристосування, а не тумблінг. */
typedef enum {
    CALIB6_MODEL_DIAGONAL = 0,  /* 3 масштаби + 3 зсуви: вистачає 6 позицій */
    CALIB6_MODEL_TRIAXIAL = 1   /* 6 елементів M + 3 зсуви: треба >= 9 позицій */
} calib6_model_t;

typedef enum {
    CALIB6_OK = 0,
    CALIB6_ERR_ARGS,
    CALIB6_ERR_FEW_POSITIONS,
    CALIB6_ERR_NOT_SPANNING,
    CALIB6_ERR_SINGULAR,
    CALIB6_ERR_NO_CONVERGENCE
} calib6_status_t;

typedef struct {
    mat3_t m;        /* M = R_align·S_ortho у нижній трикутній формі */
    vec3_t bias;     /* b_bias у тих самих одиницях, що й вимірювання */
    float  rms_rel;  /* середньоквадратична нев'язка норми, частка від g */
    int    iterations;
} calib6_result_t;

const char *calib6_status_text(calib6_status_t s);

/* Гаус-Ньютон із демпфуванням Левенберга: вписує хмару вимірів в еліпсоїд
   і шукає деформацію, що стискає його у сферу радіуса g. */
calib6_status_t calib6_solve(const vec3_t *avg, int count, float gravity,
                             calib6_model_t model, calib6_result_t *out);

/* Позиція годиться, лише якщо апарат справді стояв: розкид навколо середнього малий. */
bool calib6_still_average(const vec3_t *samples, int count, float tol, vec3_t *out_avg);

#endif /* CALIB6_H */
