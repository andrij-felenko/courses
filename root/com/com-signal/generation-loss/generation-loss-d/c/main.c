// Витяг з алгоритму аналізу SNR (C99)
double snr_aligned[11];
double snr_drift[11];

for (int gen = 1; gen <= 10; ++gen) {
    // Режим 1: Вирівняна сітка -> SNR виходить на плато (31.24 дБ)
    quantize_aligned(data_a, len, step);
    
    // Режим 2: Дрейфуюча сітка зі зсувом -> SNR падає з 31.21 дБ до 17.95 дБ
    quantize_misaligned(data_b, len, step, drift_eps);
}
