#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define MAX_DEVICES 10000
#define MAX_WAVES 8

typedef enum {
    DEV_STATE_IDLE = 0,
    DEV_STATE_ASSIGNED,
    DEV_STATE_IN_FLIGHT,
    DEV_STATE_REBOOTING,
    DEV_STATE_SUCCEEDED,
    DEV_STATE_FAILED,
    DEV_STATE_ROLLED_BACK,
    DEV_STATE_SILENCED
} DeviceState;

typedef enum {
    ENGINE_STATUS_RUNNING = 0,
    ENGINE_STATUS_SOAKING,
    ENGINE_STATUS_PAUSED_STOP_THE_LINE,
    ENGINE_STATUS_COMPLETED
} EngineStatus;

typedef struct {
    uint32_t device_id;
    DeviceState state;
    time_t state_updated_at;
    time_t lease_expires_at;
    uint32_t wave_index;
} DeviceRecord;

typedef struct {
    char name[32];
    double target_pct;
    uint32_t target_count;
    uint32_t max_in_flight;
    time_t soak_duration_sec;
    time_t soak_started_at;
} WaveConfig;

typedef struct {
    double max_failure_rate_pct;
    double max_rollback_rate_pct;
    double max_silence_rate_pct;
    uint32_t min_sample_size;
    time_t heartbeat_timeout_sec;
} SafetyThresholds;

typedef struct {
    DeviceRecord devices[MAX_DEVICES];
    uint32_t total_devices;
    
    WaveConfig waves[MAX_WAVES];
    uint32_t waves_count;
    uint32_t current_wave;
    
    SafetyThresholds safety;
    EngineStatus status;
    
    double tokens;
    double token_fill_rate;
    double token_capacity;
    time_t last_token_refill;
    
    uint32_t in_flight_count;
    uint32_t succeeded_count;
    uint32_t failed_count;
    uint32_t rolled_back_count;
    uint32_t silenced_count;
} CampaignEngine;

void engine_init(CampaignEngine *eng, uint32_t total_devs, SafetyThresholds safety) {
    memset(eng, 0, sizeof(CampaignEngine));
    eng->total_devices = (total_devs > MAX_DEVICES) ? MAX_DEVICES : total_devs;
    eng->safety = safety;
    eng->status = ENGINE_STATUS_RUNNING;
    eng->token_fill_rate = 20.0;
    eng->token_capacity = 100.0;
    eng->tokens = eng->token_capacity;
    eng->last_token_refill = time(NULL);

    for (uint32_t i = 0; i < eng->total_devices; i++) {
        eng->devices[i].device_id = 100000 + i;
        eng->devices[i].state = DEV_STATE_IDLE;
        eng->devices[i].state_updated_at = time(NULL);
    }
}

void engine_add_wave(CampaignEngine *eng, const char *name, double target_pct, 
                     uint32_t max_in_flight, time_t soak_sec) {
    if (eng->waves_count >= MAX_WAVES) return;
    WaveConfig *w = &eng->waves[eng->waves_count++];
    strncpy(w->name, name, sizeof(w->name) - 1);
    w->target_pct = target_pct;
    w->target_count = (uint32_t)(eng->total_devices * (target_pct / 100.0));
    w->max_in_flight = max_in_flight;
    w->soak_duration_sec = soak_sec;
    w->soak_started_at = 0;
}

void refill_tokens(CampaignEngine *eng, time_t now) {
    double delta = (double)(now - eng->last_token_refill);
    if (delta > 0) {
        eng->tokens += delta * eng->token_fill_rate;
        if (eng->tokens > eng->token_capacity) {
            eng->tokens = eng->token_capacity;
        }
        eng->last_token_refill = now;
    }
}

bool acquire_download_token(CampaignEngine *eng, uint32_t device_idx, time_t now) {
    if (eng->status != ENGINE_STATUS_RUNNING) return false;
    refill_tokens(eng, now);
    
    WaveConfig *wave = &eng->waves[eng->current_wave];
    if (eng->in_flight_count >= wave->max_in_flight) return false;
    if (eng->tokens < 1.0) return false;

    eng->tokens -= 1.0;
    eng->in_flight_count++;
    eng->devices[device_idx].state = DEV_STATE_IN_FLIGHT;
    eng->devices[device_idx].state_updated_at = now;
    eng->devices[device_idx].lease_expires_at = now + 1800; // 30 хвилин лізингу
    return true;
}

void evaluate_safety_and_stop_the_line(CampaignEngine *eng) {
    uint32_t evaluated = eng->succeeded_count + eng->failed_count + 
                         eng->rolled_back_count + eng->silenced_count;
    if (evaluated < eng->safety.min_sample_size) return;

    double fail_rate = ((double)eng->failed_count / evaluated) * 100.0;
    double rb_rate = ((double)eng->rolled_back_count / evaluated) * 100.0;
    double silence_rate = ((double)eng->silenced_count / evaluated) * 100.0;

    if (fail_rate > eng->safety.max_failure_rate_pct ||
        rb_rate > eng->safety.max_rollback_rate_pct ||
        silence_rate > eng->safety.max_silence_rate_pct) {
        
        eng->status = ENGINE_STATUS_PAUSED_STOP_THE_LINE;
        printf("[STOP-THE-LINE] Кампанію аварійно зупинено! Помилки: %.2f%%, Відкоти: %.2f%%, Мовчання: %.2f%%\n",
               fail_rate, rb_rate, silence_rate);
    }
}

void report_device_event(CampaignEngine *eng, uint32_t device_idx, DeviceState new_state, time_t now) {
    DeviceRecord *dev = &eng->devices[device_idx];
    if (dev->state == DEV_STATE_IN_FLIGHT || dev->state == DEV_STATE_REBOOTING) {
        if (eng->in_flight_count > 0) eng->in_flight_count--;
    }

    dev->state = new_state;
    dev->state_updated_at = now;

    if (new_state == DEV_STATE_SUCCEEDED) eng->succeeded_count++;
    else if (new_state == DEV_STATE_FAILED) eng->failed_count++;
    else if (new_state == DEV_STATE_ROLLED_BACK) eng->rolled_back_count++;

    evaluate_safety_and_stop_the_line(eng);
}

void check_silenced_devices(CampaignEngine *eng, time_t now) {
    for (uint32_t i = 0; i < eng->total_devices; i++) {
        DeviceRecord *dev = &eng->devices[i];
        if (dev->state == DEV_STATE_REBOOTING) {
            if (now - dev->state_updated_at > eng->safety.heartbeat_timeout_sec) {
                dev->state = DEV_STATE_SILENCED;
                dev->state_updated_at = now;
                eng->silenced_count++;
                if (eng->in_flight_count > 0) eng->in_flight_count--;
                evaluate_safety_and_stop_the_line(eng);
            }
        }
    }
}

void engine_tick(CampaignEngine *eng, time_t now) {
    if (eng->status == ENGINE_STATUS_PAUSED_STOP_THE_LINE || 
        eng->status == ENGINE_STATUS_COMPLETED) return;

    check_silenced_devices(eng, now);
    WaveConfig *wave = &eng->waves[eng->current_wave];

    // Призначення пристроїв у межах квоти поточної хвилі
    uint32_t assigned_in_wave = 0;
    for (uint32_t i = 0; i < wave->target_count; i++) {
        if (eng->devices[i].state == DEV_STATE_IDLE) {
            if (acquire_download_token(eng, i, now)) {
                eng->devices[i].wave_index = eng->current_wave;
            }
        }
        if (eng->devices[i].state != DEV_STATE_IDLE) {
            assigned_in_wave++;
        }
    }

    // Перевірка завершення завантажень хвилі та старт витримки (Soak Time)
    if (assigned_in_wave >= wave->target_count && eng->in_flight_count == 0) {
        if (eng->status == ENGINE_STATUS_RUNNING) {
            eng->status = ENGINE_STATUS_SOAKING;
            wave->soak_started_at = now;
            printf("[ХВИЛЯ] Хвиля '%s' перейшла у фазу витримки (Soak Time %lds)\n", 
                   wave->name, wave->soak_duration_sec);
        } else if (eng->status == ENGINE_STATUS_SOAKING) {
            if (now - wave->soak_started_at >= wave->soak_duration_sec) {
                if (eng->current_wave + 1 < eng->waves_count) {
                    eng->current_wave++;
                    eng->status = ENGINE_STATUS_RUNNING;
                    printf("[ХВИЛЯ] Успішно! Перехід на хвилю '%s'\n", eng->waves[eng->current_wave].name);
                } else {
                    eng->status = ENGINE_STATUS_COMPLETED;
                    printf("[ФІНІШ] Кампанія успішно завершена на 100%% парку!\n");
                }
            }
        }
    }
}
