#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

#define MAX_TIMELINE_EVENTS 128
#define MAX_ONCALL_TIERS    3
#define MAX_NAME_LEN        64
#define MAX_DESC_LEN        256

/* Стани життєвого циклу інциденту */
typedef enum {
    INCIDENT_STATE_TRIGGERED = 0,
    INCIDENT_STATE_ACKNOWLEDGED,
    INCIDENT_STATE_ESCALATED,
    INCIDENT_STATE_MITIGATED,
    INCIDENT_STATE_RESOLVED
} incident_state_t;

/* Рівні критичності */
typedef enum {
    SEVERITY_SEV1 = 1,
    SEVERITY_SEV2 = 2,
    SEVERITY_SEV3 = 3,
    SEVERITY_SEV4 = 4
} severity_t;

/* Запис у хронології інциденту */
typedef struct {
    struct timespec timestamp;
    char message[MAX_DESC_LEN];
    incident_state_t state_snapshot;
} timeline_event_t;

/* Інженер чергової зміни */
typedef struct {
    char name[MAX_NAME_LEN];
    char phone[MAX_NAME_LEN];
    char slack_handle[MAX_NAME_LEN];
} oncall_engineer_t;

/* Політика ескалації */
typedef struct {
    oncall_engineer_t tiers[MAX_ONCALL_TIERS];
    int total_tiers;
    int ack_timeout_sec;
} escalation_policy_t;

/* Структура керованого інциденту */
typedef struct {
    uint64_t id;
    char title[MAX_NAME_LEN];
    severity_t severity;
    incident_state_t state;
    int current_tier;
    uint32_t ack_token;
    
    escalation_policy_t policy;
    timeline_event_t timeline[MAX_TIMELINE_EVENTS];
    int timeline_count;
    
    pthread_mutex_t lock;
    pthread_cond_t state_cond;
    pthread_t timer_thread;
    bool timer_active;
    bool worker_running;
} incident_t;

static uint64_t get_current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

static const char* state_to_string(incident_state_t s) {
    switch (s) {
        case INCIDENT_STATE_TRIGGERED:    return "TRIGGERED";
        case INCIDENT_STATE_ACKNOWLEDGED: return "ACKNOWLEDGED";
        case INCIDENT_STATE_ESCALATED:    return "ESCALATED";
        case INCIDENT_STATE_MITIGATED:    return "MITIGATED";
        case INCIDENT_STATE_RESOLVED:     return "RESOLVED";
        default:                          return "UNKNOWN";
    }
}

/* Внутрішній запис події в хронологію (під захистом lock) */
static void append_timeline_locked(incident_t* inc, const char* msg) {
    if (inc->timeline_count >= MAX_TIMELINE_EVENTS) return;
    
    timeline_event_t* ev = &inc->timeline[inc->timeline_count++];
    clock_gettime(CLOCK_REALTIME, &ev->timestamp);
    ev->state_snapshot = inc->state;
    snprintf(ev->message, sizeof(ev->message), "%s", msg);
    
    printf("[%lu ms] [INC-%lu] [%s] %s\n", 
           get_current_time_ms(), inc->id, state_to_string(inc->state), msg);
}

/* Симуляція відправки пейджа черговому */
static void dispatch_pager_notification(const oncall_engineer_t* eng, const incident_t* inc) {
    printf(">>> PAGER ALERT >>> Дзвінок/SMS на %s (%s): [SEV-%d] %s. Введіть токен %u для ACK.\n",
           eng->phone, eng->name, inc->severity, inc->title, inc->ack_token);
}

/* Потік таймера ескалації */
static void* escalation_timer_worker(void* arg) {
    incident_t* inc = (incident_t*)arg;
    
    while (true) {
        pthread_mutex_lock(&inc->lock);
        
        while (inc->worker_running && 
               (inc->state == INCIDENT_STATE_ACKNOWLEDGED || 
                inc->state == INCIDENT_STATE_MITIGATED || 
                inc->state == INCIDENT_STATE_RESOLVED)) {
            pthread_cond_wait(&inc->state_cond, &inc->lock);
        }
        
        if (!inc->worker_running) {
            pthread_mutex_unlock(&inc->lock);
            break;
        }
        
        /* Обчислюємо дедлайн очікування */
        struct timespec deadline;
        clock_gettime(CLOCK_REALTIME, &deadline);
        deadline.tv_sec += inc->policy.ack_timeout_sec;
        
        int wait_res = 0;
        while (inc->worker_running && 
               (inc->state == INCIDENT_STATE_TRIGGERED || inc->state == INCIDENT_STATE_ESCALATED) &&
               wait_res == 0) {
            wait_res = pthread_cond_timedwait(&inc->state_cond, &inc->lock, &deadline);
        }
        
        if (!inc->worker_running) {
            pthread_mutex_unlock(&inc->lock);
            break;
        }
        
        if (wait_res == ETIMEDOUT && 
            (inc->state == INCIDENT_STATE_TRIGGERED || inc->state == INCIDENT_STATE_ESCALATED)) {
            
            char log_buf[MAX_DESC_LEN];
            snprintf(log_buf, sizeof(log_buf), "Дедлайн підтвердження (%d сек) вичерпано на рівні Tier-%d (%s)",
                     inc->policy.ack_timeout_sec, inc->current_tier + 1,
                     inc->policy.tiers[inc->current_tier].name);
            append_timeline_locked(inc, log_buf);
            
            if (inc->current_tier + 1 < inc->policy.total_tiers) {
                inc->current_tier++;
                inc->state = INCIDENT_STATE_ESCALATED;
                inc->ack_token = (uint32_t)(rand() % 900000 + 100000);
                
                snprintf(log_buf, sizeof(log_buf), "Ескалація на рівень Tier-%d: черговий %s",
                         inc->current_tier + 1, inc->policy.tiers[inc->current_tier].name);
                append_timeline_locked(inc, log_buf);
                
                dispatch_pager_notification(&inc->policy.tiers[inc->current_tier], inc);
            } else {
                snprintf(log_buf, sizeof(log_buf), "КРИТИЧНО: Усі рівні ескалації вичерпані! Аварійний broadcast на Incident Commander.");
                append_timeline_locked(inc, log_buf);
                inc->worker_running = false;
                pthread_mutex_unlock(&inc->lock);
                break;
            }
        }
        
        pthread_mutex_unlock(&inc->lock);
    }
    
    return NULL;
}

/* Ініціалізація інциденту */
bool incident_init(incident_t* inc, uint64_t id, const char* title, severity_t sev, const escalation_policy_t* pol) {
    if (!inc || !title || !pol) return false;
    memset(inc, 0, sizeof(*inc));
    
    inc->id = id;
    snprintf(inc->title, sizeof(inc->title), "%s", title);
    inc->severity = sev;
    inc->state = INCIDENT_STATE_TRIGGERED;
    inc->current_tier = 0;
    inc->policy = *pol;
    inc->timeline_count = 0;
    inc->worker_running = true;
    inc->ack_token = (uint32_t)(rand() % 900000 + 100000);
    
    pthread_mutex_init(&inc->lock, NULL);
    pthread_cond_init(&inc->state_cond, NULL);
    
    char log_buf[MAX_DESC_LEN];
    snprintf(log_buf, sizeof(log_buf), "Інцидент відкрито із критичністю SEV-%d. Призначено на Tier-1: %s",
             sev, inc->policy.tiers[0].name);
    
    pthread_mutex_lock(&inc->lock);
    append_timeline_locked(inc, log_buf);
    pthread_mutex_unlock(&inc->lock);
    
    dispatch_pager_notification(&inc->policy.tiers[0], inc);
    
    if (pthread_create(&inc->timer_thread, NULL, escalation_timer_worker, inc) != 0) {
        return false;
    }
    inc->timer_active = true;
    return true;
}

/* Підтвердження отримання інциденту черговим */
bool incident_acknowledge(incident_t* inc, uint32_t token, const char* responder_name) {
    pthread_mutex_lock(&inc->lock);
    
    if (inc->state != INCIDENT_STATE_TRIGGERED && inc->state != INCIDENT_STATE_ESCALATED) {
        pthread_mutex_unlock(&inc->lock);
        return false;
    }
    
    if (inc->ack_token != token) {
        char log_buf[MAX_DESC_LEN];
        snprintf(log_buf, sizeof(log_buf), "Відхилено ACK від %s: недійсний токен %u", responder_name, token);
        append_timeline_locked(inc, log_buf);
        pthread_mutex_unlock(&inc->lock);
        return false;
    }
    
    inc->state = INCIDENT_STATE_ACKNOWLEDGED;
    char log_buf[MAX_DESC_LEN];
    snprintf(log_buf, sizeof(log_buf), "Інцидент підтверджено черговим %s (рівень Tier-%d). Таймер ескалації зупинено.",
             responder_name, inc->current_tier + 1);
    append_timeline_locked(inc, log_buf);
    
    pthread_cond_broadcast(&inc->state_cond);
    pthread_mutex_unlock(&inc->lock);
    return true;
}

/* Фіксація пом'якшення інциденту (Mitigation) */
bool incident_mitigate(incident_t* inc, const char* action_taken) {
    pthread_mutex_lock(&inc->lock);
    
    if (inc->state != INCIDENT_STATE_ACKNOWLEDGED) {
        pthread_mutex_unlock(&inc->lock);
        return false;
    }
    
    inc->state = INCIDENT_STATE_MITIGATED;
    char log_buf[MAX_DESC_LEN];
    snprintf(log_buf, sizeof(log_buf), "Вплив на користувачів усунуто: %s. Початок стабілізаційного періоду.", action_taken);
    append_timeline_locked(inc, log_buf);
    
    pthread_cond_broadcast(&inc->state_cond);
    pthread_mutex_unlock(&inc->lock);
    return true;
}

/* Повне закриття інциденту */
void incident_resolve(incident_t* inc, const char* resolution_summary) {
    pthread_mutex_lock(&inc->lock);
    inc->state = INCIDENT_STATE_RESOLVED;
    inc->worker_running = false;
    
    char log_buf[MAX_DESC_LEN];
    snprintf(log_buf, sizeof(log_buf), "Інцидент успішно закрито: %s. Матеріали передано на постмортем.", resolution_summary);
    append_timeline_locked(inc, log_buf);
    
    pthread_cond_broadcast(&inc->state_cond);
    pthread_mutex_unlock(&inc->lock);
    
    if (inc->timer_active) {
        pthread_join(inc->timer_thread, NULL);
        inc->timer_active = false;
    }
    pthread_mutex_destroy(&inc->lock);
    pthread_cond_destroy(&inc->state_cond);
}
