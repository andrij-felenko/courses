#include <math.h>
// Обидві величини множаться на те саме G — відношення не зрушується
float Usig_in  = 2.0e-3f;     // сигнал на вході, В rms
float Unoise_in = 1.82e-6f;   // тепловий шум опору джерела, В rms
float G = 100.0f;             // підсилення

float Usig_out   = G * Usig_in;     // 0.200 В
float Unoise_out = G * Unoise_in;   // 1.82e-4 В

float snr_in_db  = 20.0f * log10f(Usig_in  / Unoise_in);   // ≈ 60.8 дБ
float snr_out_db = 20.0f * log10f(Usig_out / Unoise_out);  // ≈ 60.8 дБ — те саме!
