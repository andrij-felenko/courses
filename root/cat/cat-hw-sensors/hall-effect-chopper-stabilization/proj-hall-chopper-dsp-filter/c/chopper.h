#ifndef CHOPPER_H
#define CHOPPER_H

#include <stdint.h>

#define BUFFER_SIZE 16
#define FIR_TAPS 4

typedef struct {
    int32_t buffer[BUFFER_SIZE];
    uint8_t head;
    int32_t sum;
} MovingAverage;

typedef struct {
    int32_t history[FIR_TAPS];
    uint8_t index;
} FirFilter;

void Chopper_Init(MovingAverage *ma, FirFilter *fir);
int32_t Chopper_Process(int32_t phase0_val, int32_t phase1_val, MovingAverage *ma, FirFilter *fir);

#endif // CHOPPER_H
