#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define MAX_TOKEN_LEN 256

typedef struct {
    char access_token[MAX_TOKEN_LEN];
    char refresh_token[MAX_TOKEN_LEN];
    time_t expires_at;
} token_data_t;

typedef struct {
    token_data_t data;
    bool has_data;
    bool is_refreshing;
    double skew_sec;
    pthread_mutex_t lock;
    pthread_cond_t cond;
} c_auth_interceptor_t;

void c_auth_init(c_auth_interceptor_t *it, double skew) {
    memset(&it->data, 0, sizeof(token_data_t));
    it->has_data = false;
    it->is_refreshing = false;
    it->skew_sec = skew;
    pthread_mutex_init(&it->lock, NULL);
    pthread_cond_init(&it->cond, NULL);
}

static bool perform_oauth_refresh(const char *old_refresh, token_data_t *out_data) {
    usleep(50000); // 50 мс затримки виклику
    time_t now = time(NULL);
    snprintf(out_data->access_token, MAX_TOKEN_LEN, "c_acc_%ld", (long)now);
    snprintf(out_data->refresh_token, MAX_TOKEN_LEN, "c_ref_%ld", (long)now);
    out_data->expires_at = now + 900;
    return true;
}

bool c_auth_get_token(c_auth_interceptor_t *it, char *dest, size_t dest_len) {
    pthread_mutex_lock(&it->lock);

    while (1) {
        if (!it->has_data) {
            pthread_mutex_unlock(&it->lock);
            return false;
        }

        time_t now = time(NULL);
        bool expired = (now >= (it->data.expires_at - (time_t)it->skew_sec));

        if (!expired) {
            strncpy(dest, it->data.access_token, dest_len - 1);
            dest[dest_len - 1] = '\0';
            pthread_mutex_unlock(&it->lock);
            return true;
        }

        if (!it->is_refreshing) {
            it->is_refreshing = true;
            break;
        } else {
            pthread_cond_wait(&it->cond, &it->lock);
        }
    }

    char active_refresh[MAX_TOKEN_LEN];
    strncpy(active_refresh, it->data.refresh_token, MAX_TOKEN_LEN - 1);
    pthread_mutex_unlock(&it->lock);

    token_data_t fresh_data;
    bool success = perform_oauth_refresh(active_refresh, &fresh_data);

    pthread_mutex_lock(&it->lock);
    if (success) {
        it->data = fresh_data;
        strncpy(dest, it->data.access_token, dest_len - 1);
        dest[dest_len - 1] = '\0';
    }
    it->is_refreshing = false;
    pthread_cond_broadcast(&it->cond);
    pthread_mutex_unlock(&it->lock);

    return success;
}
