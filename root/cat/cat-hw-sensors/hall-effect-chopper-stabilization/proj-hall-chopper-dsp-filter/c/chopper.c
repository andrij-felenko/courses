#include "chopper.h"

// Коефіцієнти FIR-фільтра (сума = 1024, щоб нормалізувати через бітовий зсув)
static const int32_t fir_coeffs[FIR_TAPS] = { 102, 410, 410, 102 };

void Chopper_Init(MovingAverage *ma, FirFilter *fir) {
    ma->head = 0;
    ma->sum = 0;
    for (int i = 0; i < BUFFER_SIZE; i++) {
        ma->buffer[i] = 0;
    }

    fir->index = 0;
    for (int i = 0; i < FIR_TAPS; i++) {
        fir->history[i] = 0;
    }
}

static int32_t MovingAverage_Process(MovingAverage *ma, int32_t new_val) {
    ma->sum -= ma->buffer[ma->head];
    ma->buffer[ma->head] = new_val;
    ma->sum += new_val;
    ma->head = (ma->head + 1) % BUFFER_SIZE;
    
    return ma->sum / BUFFER_SIZE;
}

static int32_t Fir_Process(FirFilter *fir, int32_t new_val) {
    fir->history[fir->index] = new_val;
    int32_t out = 0;
    
    for (int i = 0; i < FIR_TAPS; i++) {
        int idx = (fir->index - i + FIR_TAPS) % FIR_TAPS;
        out += fir->history[idx] * fir_coeffs[i];
    }
    
    fir->index = (fir->index + 1) % FIR_TAPS;
    
    // Ділимо на 1024 (2^10) для нормалізації
    return out >> 10;
}

int32_t Chopper_Process(int32_t phase0_val, int32_t phase1_val, MovingAverage *ma, FirFilter *fir) {
    // Демодуляція: зміщення нуля взаємознищується, сигнал подвоюється
    // Фаза 0: V_sensor = V_offset + V_hall
    // Фаза 1: V_sensor = V_offset - V_hall
    // v_hall = (Фаза 0 - Фаза 1) / 2
    int32_t v_hall_raw = (phase0_val - phase1_val) / 2;
    
    // Придушення низькочастотних шумів та флуктуацій
    int32_t ma_out = MovingAverage_Process(ma, v_hall_raw);
    
    // Згладжування сигналу
    return Fir_Process(fir, ma_out);
}
