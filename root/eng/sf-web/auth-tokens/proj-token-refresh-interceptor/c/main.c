#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

#define TOKEN_BUF_LEN 256

typedef struct {
    char access_token[TOKEN_BUF_LEN];
    char refresh_token[TOKEN_BUF_LEN];
    time_t expires_at;
} token_state_t;

typedef struct {
    token_state_t state;
    bool has_tokens;
    bool is_refreshing;
    double clock_skew_sec;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
} auth_interceptor_t;

void auth_interceptor_init(auth_interceptor_t *interceptor, double skew_sec) {
    memset(&interceptor->state, 0, sizeof(token_state_t));
    interceptor->has_tokens = false;
    interceptor->is_refreshing = false;
    interceptor->clock_skew_sec = skew_sec;
    pthread_mutex_init(&interceptor->mutex, NULL);
    pthread_cond_init(&interceptor->cond, NULL);
}

void auth_interceptor_set_tokens(auth_interceptor_t *in, const char *acc, const char *ref, int expires_in) {
    pthread_mutex_lock(&in->mutex);
    strncpy(in->state.access_token, acc, TOKEN_BUF_LEN - 1);
    strncpy(in->state.refresh_token, ref, TOKEN_BUF_LEN - 1);
    in->state.expires_at = time(NULL) + expires_in;
    in->has_tokens = true;
    pthread_mutex_unlock(&in->mutex);
}

static bool perform_network_refresh(const char *old_ref, token_state_t *out_state) {
    usleep(50000); // Імітація виклику POST /oauth/token (50 мс)
    time_t now = time(NULL);
    snprintf(out_state->access_token, TOKEN_BUF_LEN, "c_acc_%ld", (long)now);
    snprintf(out_state->refresh_token, TOKEN_BUF_LEN, "c_ref_%ld", (long)now);
    out_state->expires_at = now + 900;
    return true;
}

bool auth_interceptor_get_token(auth_interceptor_t *in, char *out_buf, size_t buf_size) {
    pthread_mutex_lock(&in->mutex);

    while (1) {
        if (!in->has_tokens) {
            pthread_mutex_unlock(&in->mutex);
            return false;
        }

        time_t now = time(NULL);
        bool is_expired = (now >= (in->state.expires_at - (time_t)in->clock_skew_sec));

        if (!is_expired) {
            strncpy(out_buf, in->state.access_token, buf_size - 1);
            out_buf[buf_size - 1] = '\0';
            pthread_mutex_unlock(&in->mutex);
            return true;
        }

        if (!in->is_refreshing) {
            in->is_refreshing = true;
            break;
        } else {
            pthread_cond_wait(&in->cond, &in->mutex);
        }
    }

    char current_refresh[TOKEN_BUF_LEN];
    strncpy(current_refresh, in->state.refresh_token, TOKEN_BUF_LEN - 1);
    pthread_mutex_unlock(&in->mutex);

    token_state_t new_state;
    bool ok = perform_network_refresh(current_refresh, &new_state);

    pthread_mutex_lock(&in->mutex);
    if (ok) {
        in->state = new_state;
        strncpy(out_buf, in->state.access_token, buf_size - 1);
        out_buf[buf_size - 1] = '\0';
    }
    in->is_refreshing = false;
    pthread_cond_broadcast(&in->cond);
    pthread_mutex_unlock(&in->mutex);

    return ok;
}
