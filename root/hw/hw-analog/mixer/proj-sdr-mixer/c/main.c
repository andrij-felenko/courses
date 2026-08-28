#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#define NCO_TABLE_SIZE 1024
#define PI 3.14159265358979323846

/* Структура цифрового квадратурного змішувача */
typedef struct {
    float sin_table[NCO_TABLE_SIZE];
    float cos_table[NCO_TABLE_SIZE];
    uint32_t phase_accumulator;
    uint32_t phase_increment;
} sdr_mixer_t;

/* Ініціалізація змішувача та генерація таблиць NCO */
void sdr_mixer_init(sdr_mixer_t *mixer, double sample_rate, double target_freq) {
    int i;
    for (i = 0; i < NCO_TABLE_SIZE; i++) {
        double angle = (2.0 * PI * i) / NCO_TABLE_SIZE;
        mixer->sin_table[i] = (float)sin(angle);
        mixer->cos_table[i] = (float)cos(angle);
    }
    
    mixer->phase_accumulator = 0;
    /* Крок фази у 32-бітному фіксованому форматі */
    double norm_freq = target_freq / sample_rate;
    mixer->phase_increment = (uint32_t)(norm_freq * 4294967296.0);
}

/* Обробка буфера вхідних відліків */
void sdr_mixer_process(sdr_mixer_t *mixer, const float *in_rf, 
                       float *out_i, float *out_q, size_t count) {
    size_t n;
    for (n = 0; n < count; n++) {
        /* Отримання 10-бітного індексу таблиці з старших бітів акумулятора */
        uint32_t index = mixer->phase_accumulator >> (32 - 10);
        
        float cos_val = mixer->cos_table[index];
        float sin_val = mixer->sin_table[index];
        
        float sample = in_rf[n];
        out_i[n] = sample * cos_val;
        out_q[n] = sample * (-sin_val);
        
        /* Оновлення фазового акумулятора */
        mixer->phase_accumulator += mixer->phase_increment;
    }
}
