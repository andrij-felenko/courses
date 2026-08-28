#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Комплексний відлік базової смуги (I/Q) */
typedef struct {
    float i;
    float q;
} iq_sample_t;

/* Стан кореляційного інтегратора */
typedef struct {
    uint32_t fs_hz;            /* Частота дискретизації, Гц */
    uint32_t n_coh;            /* Кількість відліків в одному когерентному вікні T_coh */
    uint32_t m_blocks;         /* Кількість некогерентних блоків у T_meas */
    
    /* Параметри доплерівського NCO */
    float doppler_hz;          /* Поточна оцінка доплерівської частоти */
    float nco_phase_rad;       /* Поточна фаза генератора NCO [0, 2pi) */
    float phase_step_rad;      /* Крок фази за один відлік */
    
    /* Проміжні когерентні акумулятори */
    float acc_coh_e_i;
    float acc_coh_e_q;
    float acc_coh_p_i;
    float acc_coh_p_q;
    float acc_coh_l_i;
    float acc_coh_l_q;
    uint32_t coh_counter;
    
    /* Некогерентні накопичувачі енергії за T_meas */
    float power_early;
    float power_prompt;
    float power_late;
    uint32_t block_counter;
    
    /* Результати останнього повного вимірювання */
    float last_discriminator_err;
    float estimated_snr_db;
    bool measurement_ready;
} correlator_integrator_t;

/* Ініціалізація структури корелятора */
void correlator_init(correlator_integrator_t *self, uint32_t fs_hz, 
                     float t_coh_sec, uint32_t m_blocks, float initial_doppler_hz) {
    self->fs_hz = fs_hz;
    self->n_coh = (uint32_t)(fs_hz * t_coh_sec + 0.5f);
    if (self->n_coh < 1) self->n_coh = 1;
    self->m_blocks = (m_blocks > 0) ? m_blocks : 1;
    
    self->doppler_hz = initial_doppler_hz;
    self->nco_phase_rad = 0.0f;
    self->phase_step_rad = (float)(2.0 * M_PI * initial_doppler_hz / fs_hz);
    
    self->acc_coh_e_i = 0.0f; self->acc_coh_e_q = 0.0f;
    self->acc_coh_p_i = 0.0f; self->acc_coh_p_q = 0.0f;
    self->acc_coh_l_i = 0.0f; self->acc_coh_l_q = 0.0f;
    self->coh_counter = 0;
    
    self->power_early = 0.0f;
    self->power_prompt = 0.0f;
    self->power_late = 0.0f;
    self->block_counter = 0;
    
    self->last_discriminator_err = 0.0f;
    self->estimated_snr_db = 0.0f;
    self->measurement_ready = false;
}

/* Оновлення поточної частоти Доплера для NCO */
void correlator_set_doppler(correlator_integrator_t *self, float doppler_hz) {
    self->doppler_hz = doppler_hz;
    self->phase_step_rad = (float)(2.0 * M_PI * doppler_hz / self->fs_hz);
}

/* Обробка одного відліку вхідного сигналу та значень трьох кодових копій */
bool correlator_process_sample(correlator_integrator_t *self, iq_sample_t raw,
                               float code_early, float code_prompt, float code_late) {
    self->measurement_ready = false;
    
    /* 1. Фазове зняття Доплера через NCO: r_bb = raw * exp(-j * phi) */
    float cos_phi = cosf(self->nco_phase_rad);
    float sin_phi = sinf(self->nco_phase_rad);
    
    float rot_i = raw.i * cos_phi + raw.q * sin_phi;
    float rot_q = raw.q * cos_phi - raw.i * sin_phi;
    
    /* Оновлення фази NCO на один крок */
    self->nco_phase_rad += self->phase_step_rad;
    if (self->nco_phase_rad >= (float)(2.0 * M_PI)) {
        self->nco_phase_rad -= (float)(2.0 * M_PI);
    } else if (self->nco_phase_rad < 0.0f) {
        self->nco_phase_rad += (float)(2.0 * M_PI);
    }
    
    /* 2. Когерентне накопичення для трьох плечей */
    self->acc_coh_e_i += rot_i * code_early;
    self->acc_coh_e_q += rot_q * code_early;
    
    self->acc_coh_p_i += rot_i * code_prompt;
    self->acc_coh_p_q += rot_q * code_prompt;
    
    self->acc_coh_l_i += rot_i * code_late;
    self->acc_coh_l_q += rot_q * code_late;
    
    self->coh_counter++;
    
    /* 3. Завершення когерентного вікна T_coh */
    if (self->coh_counter >= self->n_coh) {
        /* Обчислення потужностей трьох плечей за когерентний блок */
        float blk_pwr_e = self->acc_coh_e_i * self->acc_coh_e_i + 
                          self->acc_coh_e_q * self->acc_coh_e_q;
        float blk_pwr_p = self->acc_coh_p_i * self->acc_coh_p_i + 
                          self->acc_coh_p_q * self->acc_coh_p_q;
        float blk_pwr_l = self->acc_coh_l_i * self->acc_coh_l_i + 
                          self->acc_coh_l_q * self->acc_coh_l_q;
        
        /* Додавання до некогерентних акумуляторів */
        self->power_early  += blk_pwr_e;
        self->power_prompt += blk_pwr_p;
        self->power_late   += blk_pwr_l;
        
        /* Скидання когерентних акумуляторів */
        self->acc_coh_e_i = 0.0f; self->acc_coh_e_q = 0.0f;
        self->acc_coh_p_i = 0.0f; self->acc_coh_p_q = 0.0f;
        self->acc_coh_l_i = 0.0f; self->acc_coh_l_q = 0.0f;
        self->coh_counter = 0;
        self->block_counter++;
        
        /* 4. Завершення повного інтервалу вимірювання T_meas = M * T_coh */
        if (self->block_counter >= self->m_blocks) {
            float sum_el = self->power_early + self->power_late;
            if (sum_el > 1e-12f) {
                /* Нормований дискримінатор похибки затримки NEMLP */
                self->last_discriminator_err = (self->power_early - self->power_late) / sum_el;
            } else {
                self->last_discriminator_err = 0.0f;
            }
            
            /* Оцінка вихідного відношення сигнал/шум */
            float noise_floor = 0.5f * (self->power_early + self->power_late);
            if (noise_floor > 1e-12f && self->power_prompt > noise_floor) {
                float snr_lin = (self->power_prompt - noise_floor) / noise_floor;
                self->estimated_snr_db = 10.0f * log10f(snr_lin);
            } else {
                self->estimated_snr_db = -30.0f;
            }
            
            /* Скидання некогерентних акумуляторів для наступного T_meas */
            self->power_early = 0.0f;
            self->power_prompt = 0.0f;
            self->power_late = 0.0f;
            self->block_counter = 0;
            self->measurement_ready = true;
        }
    }
    
    return self->measurement_ready;
}
