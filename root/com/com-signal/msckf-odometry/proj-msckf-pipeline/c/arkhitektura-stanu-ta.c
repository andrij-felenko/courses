#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_SLIDING_WINDOW 20
#define IMU_STATE_DIM 15
#define POSE_STATE_DIM 6

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double w, x, y, z;
} Quat;

typedef struct {
    Vec3 pos;       /* положення у світовій системі, м */
    Vec3 vel;       /* лінійна швидкість, м/с */
    Quat att;       /* орієнтація корпусу (кватерніон) */
    Vec3 bg;        /* зсув нуля гіроскопа, рад/с */
    Vec3 ba;        /* зсув нуля акселерометра, м/с² */
} ImuState;

typedef struct {
    double timestamp;
    Vec3 pos;       /* положення камери у світовій системі */
    Quat att;       /* орієнтація камери */
} CameraPose;

typedef struct {
    int pose_idx;   /* індекс пози камери у вікні */
    double u, v;    /* нормовані координати на площині камери */
} FeatureObservation;

typedef struct {
    int id;
    int obs_count;
    FeatureObservation obs[MAX_SLIDING_WINDOW];
} FeatureTrack;

typedef struct {
    ImuState imu;
    CameraPose window[MAX_SLIDING_WINDOW];
    int window_size;
    
    /* Матриця коваріацій P: максимальний розмір (15 + 6*N) */
    int cov_dim;
    double P[(IMU_STATE_DIM + MAX_SLIDING_WINDOW * POSE_STATE_DIM) * 
             (IMU_STATE_DIM + MAX_SLIDING_WINDOW * POSE_STATE_DIM)];
} MsckfFilter;
